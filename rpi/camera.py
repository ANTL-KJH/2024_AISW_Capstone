from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import asyncio
from picamera2 import Picamera2
import cv2
import numpy as np

app = FastAPI()

# Picamera2 객체 초기화
picam2 = Picamera2()

# 카메라 설정
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# 영상 데이터를 생성하는 함수
async def generate_video_frames():
    while True:
        # 프레임 캡처
        frame = picam2.capture_array()  # Capture frame as a numpy array

        # 프레임을 JPEG 형식으로 인코딩
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # 스트림으로 프레임 반환
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        await asyncio.sleep(0.03)  # 약 30 FPS로 전송

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_video_frames(), media_type="multipart/x-mixed-replace; boundary=frame")