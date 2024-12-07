from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
from picamera2 import Picamera2
import cv2
import numpy as np
from datetime import datetime

app = FastAPI()

# Picamera2 객체 초기화
picam2 = Picamera2()

# 카메라 설정
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# 로그 데이터 관리
logs = ["one", "two", "three", "four"]  # 로그 메시지 리스트
current_index = 0  # 현재 로그 인덱스


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


@app.get("/api/logs")
async def get_logs():
    """
    로그 데이터를 순차적으로 반환.
    클라이언트가 호출할 때마다 다음 로그를 제공.
    """
    global current_index
    if current_index < len(logs):
        log_message = logs[current_index]
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "message": log_message
        }
        current_index += 1
        return JSONResponse(content=[log_data])
    else:
        return JSONResponse(content=[])  # 모든 로그를 제공한 이후 빈 배열 반환
