import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter, load_delegate
from picamera2 import Picamera2

from pycoral.utils.edgetpu import make_interpreter
from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects



# 모델 및 레이블 파일 경로
MODEL_PATH = "best_saved_model/best_float16_edgetpu.tflite"
LABELS_PATH = "best_saved_model/labels.txt"

# Edge TPU 인터프리터 로드
interpreter = Interpreter(
    model_path=MODEL_PATH,
    experimental_delegates=[load_delegate("libedgetpu.so.1")]
)
interpreter.allocate_tensors()

# 입력 및 출력 텐서 정보
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_shape = input_details[0]['shape'][1:3]

# 레이블 로드 함수
def load_labels(label_path):
    with open(label_path, "r") as f:
        return [line.strip() for line in f.readlines()]


labels = load_labels(LABELS_PATH)


def preprocess_image(image, input_size):
    # RGBA → RGB 변환
    if image.shape[2] == 4:  # RGBA 채널 확인
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

    # 이미지 리사이즈
    img = cv2.resize(image, input_size)

    # 정량화된 모델에 맞게 데이터 변환
    input_type = input_details[0]['dtype']
    if input_type == np.uint8:
        scale, zero_point = input_details[0]['quantization']
        img = img / 255.0  # 정규화
        img = (img / scale + zero_point).astype(np.uint8)  # 정량화 적용
    else:
        img = img.astype(np.float32) / 255.0  # FLOAT32 모델의 경우

    # 배치 차원 추가 (4D 텐서로 변환)
    img = np.expand_dims(img, axis=0)
    return img


def process_output(output_data, threshold=0.5):
    boxes, classes, scores = output_data
    results = []
    for i in range(len(scores)):
        if scores[i] >= threshold:
            results.append({
                "box": boxes[i],
                "class": int(classes[i]),
                "score": float(scores[i]),
            })
    return results


def detect_objects(image, threshold=0.5):
    # 입력 데이터 전처리
    input_data = preprocess_image(image, input_size(interpreter))

    # 모델 실행
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # 모델 출력 가져오기 및 처리
    objects = get_objects(interpreter, threshold)
    return objects


def draw_results(image, results):
    height, width, _ = image.shape
    for result in results:
        ymin, xmin, ymax, xmax = result["box"]
        class_id = result["class"]
        score = result["score"]

        xmin = int(xmin * width)
        xmax = int(xmax * width)
        ymin = int(ymin * height)
        ymax = int(ymax * height)

        label = f"{labels[class_id]}: {score:.2f}"
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    return image


def main():
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(camera_config)
    picam2.start()

    print("카메라 실행 중입니다. ESC 키를 눌러 종료하세요.")

    try:
        while True:
            frame = picam2.capture_array()
            results = detect_objects(frame)
            result_image = draw_results(frame, results)
            cv2.imshow("Detection", result_image)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC 키
                print("프로그램 종료")
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
