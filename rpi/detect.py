import cv2
import numpy as np
import tensorflow.lite as tflite

# 모델 및 레이블 파일 경로
MODEL_PATH = "yolov8m_saved_model/yolov8m_float16.tflite"
LABELS_PATH = "yolov8m_saved_model/labels.txt"  # 모델의 클래스 레이블 파일 (필수)

# TFLite 인터프리터 로드
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# 입력 및 출력 텐서 정보 가져오기
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# 모델 입력 크기 (예: 640x640)
input_shape = input_details[0]['shape'][1:3]

# 레이블 로드
def load_labels(label_path):
    with open(label_path, "r") as f:
        return [line.strip() for line in f.readlines()]

labels = load_labels(LABELS_PATH)

# 이미지 전처리
def preprocess_image(image, input_size):
    img = cv2.resize(image, input_size)
    img = img.astype(np.float32) / 255.0  # 정규화
    img = np.expand_dims(img, axis=0)    # 배치 차원 추가
    return img

# 결과 처리
def process_output(output_data, threshold=0.5):
    boxes, classes, scores = output_data
    results = []
    for i in range(len(scores)):
        if scores[i] >= threshold:
            results.append({
                "box": boxes[i],  # [ymin, xmin, ymax, xmax]
                "class": int(classes[i]),
                "score": float(scores[i])
            })
    return results

# 탐지 함수
def detect_objects(image):
    # 입력 데이터 전처리
    input_data = preprocess_image(image, input_shape)

    # 모델 실행
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # 출력 데이터 가져오기
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    classes = interpreter.get_tensor(output_details[1]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]

    # 탐지 결과 처리
    return process_output((boxes, classes, scores))

# 결과 시각화
def draw_results(image, results):
    height, width, _ = image.shape
    for result in results:
        ymin, xmin, ymax, xmax = result["box"]
        class_id = result["class"]
        score = result["score"]

        # 좌표 변환
        xmin = int(xmin * width)
        xmax = int(xmax * width)
        ymin = int(ymin * height)
        ymax = int(ymax * height)

        # 박스 및 레이블 그리기
        label = f"{labels[class_id]}: {score:.2f}"
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    return image

# 메인 함수
def main():
    # 카메라 또는 이미지 파일에서 입력 받기
    cap = cv2.VideoCapture(0)  # USB 카메라 사용
    # cap = cv2.VideoCapture('test_image.jpg')  # 이미지 파일 사용

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 객체 탐지 수행
        results = detect_objects(frame)

        # 결과 시각화
        result_image = draw_results(frame, results)

        # 화면에 결과 출력
        cv2.imshow('Detection', result_image)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
