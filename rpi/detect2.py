from edge_tpu_silva import process_detection
from picamera2 import Picamera2
import cv2
import numpy as np

# 모델 파일 및 설정
model_path = '192_yolov8n_full_integer_quant_edgetpu.tflite'
imgsz = 192

# Picamera2 객체 생성
picam2 = Picamera2()

# 카메라 구성 설정
camera_config = picam2.create_preview_configuration(main={"size": (imgsz, imgsz)})
picam2.configure(camera_config)

# 카메라 시작
picam2.start()

# 카메라 프레임 저장을 위한 버퍼 초기화
frame_buffer = np.empty((imgsz, imgsz, 3), dtype=np.uint8)

try:
    print("Press 'ESC' in the OpenCV window to exit.")

    while True:
        # 카메라에서 프레임 캡처
        frame = picam2.capture_array()

        # 프레임 크기 확인
        print(f"Captured frame size: {frame.shape}")

        # 모델 입력 형식으로 전처리
        input_data = np.expand_dims(frame, axis=0)  # 배치 차원 추가

        # 객체 탐지 수행
        outs = process_detection(model_path, input_data, imgsz)

        # 탐지 결과 시각화
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # OpenCV는 BGR 형식 사용

        # 프레임 크기 확인 (디버깅 용)
        print(f"Frame BGR size: {frame_bgr.shape}")

        for result in outs:
            box, cls, score = result["box"], result["class"], result["score"]

            # 박스 좌표 변환
            ymin, xmin, ymax, xmax = box
            xmin = int(xmin * frame_bgr.shape[1])
            xmax = int(xmax * frame_bgr.shape[1])
            ymin = int(ymin * frame_bgr.shape[0])
            ymax = int(ymax * frame_bgr.shape[0])

            # 좌표 값이 이미지 크기를 벗어나지 않도록 제한
            xmin = max(0, xmin)
            ymin = max(0, ymin)
            xmax = min(frame_bgr.shape[1] - 1, xmax)
            ymax = min(frame_bgr.shape[0] - 1, ymax)

            # 박스 및 레이블 그리기
            #label = f"Class {cls}: {score:.2f}"
            #cv2.rectangle(frame_bgr, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            #cv2.putText(frame_bgr, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 결과 표시
        cv2.imshow("Object Detection", frame_bgr)

        # ESC 키로 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    # 리소스 정리
    picam2.stop()
    cv2.destroyAllWindows()
