import cv2
import numpy as np
from pycoral.utils.edgetpu import make_interpreter
from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.adapters.detect import BBox

# 설정
MODEL_PATH = "192_yolo_v8n_full_integer_quant_edgetpy.tflite"  # 모델 경로
VIDEO_PATH = "videoplayback.mp4"  # 입력 동영상 경로
OUTPUT_PATH = "output_video.mp4"  # 결과 저장 경로
INPUT_RES = (192, 192)  # 모델 입력 해상도
THRESHOLD = 0.5  # 탐지 임계값

# Edge TPU 인터프리터 생성
interpreter = make_interpreter(MODEL_PATH)
interpreter.allocate_tensors()

# 입력 크기 확인
input_hw = input_size(interpreter)

# 비디오 캡처 설정
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("동영상을 열 수 없습니다.")
    exit()

# 비디오 출력 설정
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (frame_width, frame_height))

# 동영상 처리
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 이미지 전처리
    resized_frame = cv2.resize(frame, input_hw)
    input_data = np.expand_dims(resized_frame.astype(np.uint8), axis=0)

    # 모델 실행
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_data)
    interpreter.invoke()

    # 결과 가져오기
    objs = get_objects(interpreter, THRESHOLD)

    # 탐지 결과 그리기
    for obj in objs:
        bbox = obj.bbox
        cv2.rectangle(
            frame, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), (0, 255, 0), 2
        )
        label = f"{obj.id}: {obj.score:.2f}"
        cv2.putText(
            frame, label, (bbox.xmin, bbox.ymin - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2
        )

    # 결과 프레임 저장
    out.write(frame)

    # 결과 프레임 디스플레이 (옵션)
    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC 키로 종료
        break

# 자원 해제
cap.release()
out.release()
cv2.destroyAllWindows()
