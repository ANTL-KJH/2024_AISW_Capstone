from ultralytics import YOLO

# 모델 로드
model = YOLO('yolov8m.pt')

# 모델 변환
model.export(format='tflite')  # TensorFlow Lite로 변환
