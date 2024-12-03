from edge_tpu_silva import process_segmentation
from picamera2 import Picamera2
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

# 동영상 스트리밍 처리
try:
    while True:
        # 카메라에서 프레임 캡처
        frame = picam2.capture_array()

        # 객체 분할 수행
        # input_path에 "Camera(0)"을 전달하여 카메라로부터 직접 입력을 받음
        outs = process_segmentation(model_path=model_path, input_path="Camera(0)", imgsz=imgsz)

        # outs를 활용한 추가 처리가 필요하면 여기에서 진행
        # 예: 분할된 객체의 정보 활용 등

finally:
    # 카메라 종료 및 자원 해제
    picam2.stop()
