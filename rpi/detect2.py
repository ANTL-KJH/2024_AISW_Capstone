from edge_tpu_silva import process_detection
from picamera2 import Picamera2
import cv2
import numpy as np

# 모델 파일 및 설정
model_path = '192_yolov8n_full_integer_quant_edgetpu.tflite'
imgsz = 192

# Picamera2 초기화
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (imgsz, imgsz)})
picam2.configure(camera_config)
picam2.start()

try:
    print("Press 'ESC' to exit.")
    while True:
        # Picam에서 프레임 캡처
        frame = picam2.capture_array()

        # 모델 입력 형식으로 전처리
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 모델이 RGB 포맷일 경우 변환
        input_data = np.expand_dims(rgb_frame, axis=0)  # 배치 차원 추가

        # 객체 탐지 수행
        outs = process_detection(model_path, input_data, imgsz)

        # 탐지 결과 시각화
        for result in outs:
            box, cls, score = result["box"], result["class"], result["score"]

            # 박스 좌표 변환
            ymin, xmin, ymax, xmax = box
            xmin = int(xmin * frame.shape[1])
            xmax = int(xmax * frame.shape[1])
            ymin = int(ymin * frame.shape[0])
            ymax = int(ymax * frame.shape[0])

            # 박스 및 레이블 그리기
            label = f"Class {cls}: {score:.2f}"
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 결과 표시
        cv2.imshow("Object Detection", frame)

        # ESC 키로 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    # 리소스 정리
    picam2.stop()
    cv2.destroyAllWindows()
