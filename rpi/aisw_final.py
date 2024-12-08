from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
from picamera2 import Picamera2
import cv2
import numpy as np
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from edge_tpu_silva import process_detection
import threading
import time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Picamera2 객체 초기화
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 320)})
picam2.configure(camera_config)
picam2.start()

# 모델 경로 설정
model_path = 'pbest_edgetpu.tflite'
imgsz = 320
chk = False


async def generate_video_frames():
    global chk
    while True:
        frame = picam2.capture_array()
        frame = cv2.flip(frame, 0)  # 상하 반전

        # 객체 탐지 수행
        outs = process_detection(model_path=model_path, input_path=frame, imgsz=imgsz)

        for detection, inference_time in outs:
            try:
                detection_info = detection[0]
                class_id = int(detection_info['id'])
                label = detection_info['label']
                score = detection_info['conf']

                if label == "Deer" or label == "Wildboar":
                    chk = True
                else:
                    chk = False

                if score >= 0.5:
                    bbox = detection_info['bbox']
                    x1, y1, x2, y2 = map(int, bbox)

                    # 바운딩 박스 그리기
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    label_text = f"{label} ({score:.2f})"
                    cv2.putText(frame, label_text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            except Exception as e:
                print(f"Error processing detection: {e}")

        # 프레임을 JPEG 형식으로 인코딩
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # 스트림으로 프레임 반환
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        await asyncio.sleep(0.03)  # 약 30 FPS


@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_video_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/logs")
async def get_logs():
    """
    로그 데이터를 반환. (예: "antl")
    """
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "message": "antl"
    }
    return JSONResponse(content=[log_data])
