from fastapi import FastAPI, Response
import cv2
import asyncio

app = FastAPI()

# 카메라 초기화
camera = cv2.VideoCapture(0)  # 0번 카메라 (기본 웹캠 사용)

# 영상 데이터를 생성하는 함수
async def generate_video_frames():
    while True:
        success, frame = camera.read()
            if not success:
            break
        # 프레임을 JPEG 형식으로 인코딩
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        # 스트림으로 프레임 반환
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        await asyncio.sleep(0.03)  # 약 30 FPS로 전송

@app.get("/video_feed")
async def video_feed():
    return Response(generate_video_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
