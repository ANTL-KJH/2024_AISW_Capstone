from edge_tpu_silva import process_detection
import picamera
import cv2
import numpy as np
import time

# 모델 파일 및 설정
model_path = '192_yolov8n_full_integer_quant_edgetpu.tflite'
imgsz = 192

# Picamera 초기화
camera = picamera.PiCamera()
camera.resolution = (imgsz, imgsz)
camera.framerate = 30

# 카메라 프레임 저장을 위한 버퍼 초기화
frame_buffer = np.empty((imgsz, imgsz, 3), dtype=np.uint8)

try:
    print("Press 'ESC' in the OpenCV window to exit.")

    while True:
        # 카메라에서 프레임 캡처
        camera.capture(frame_buffer, format='rgb', use_video_port=True)

        # 모델 입력 형식으로 전처리
        input_data = np.expand_dims(frame_buffer, axis=0)  # 배치 차원 추가

        # 객체 탐지 수행
        outs = process_detection(model_path, input_data, imgsz)

        # 탐지 결과 시각화
        frame_bgr = cv2.cvtColor(frame_buffer, cv2.COLOR_RGB2BGR)  # OpenCV는 BGR 형식 사용
        for result in outs:
            box, cls, score = result["box"], result["class"], result["score"]

            # 박스 좌표 변환
            ymin, xmin, ymax, xmax = box
            xmin = int(xmin * frame_bgr.shape[1])
            xmax = int(xmax * frame_bgr.shape[1])
            ymin = int(ymin * frame_bgr.shape[0])
            ymax = int(ymax * frame_bgr.shape[0])

            # 박스 및 레이블 그리기
            label = f"Class {cls}: {score:.2f}"
            cv2.rectangle(frame_bgr, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(frame_bgr, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 결과 표시
        cv2.imshow("Object Detection", frame_bgr)

        # ESC 키로 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    # 리소스 정리
    camera.close()
    cv2.destroyAllWindows()
