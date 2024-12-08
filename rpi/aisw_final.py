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
import RPi.GPIO as GPIO
from rpi_ws281x import PixelStrip, Color

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GPIO 초기화
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# 충격 센서 및 모터 핀 설정
vibPinLeft = 10
vibPinRight = 12
CHECK_ON = 1
GPIO.setup(vibPinLeft, GPIO.IN)
GPIO.setup(vibPinRight, GPIO.IN)

SERVO_MAX_DUTY = 12
SERVO_MIN_DUTY = 3
servoPin1 = 16  # Servo motor pin
GPIO.setup(servoPin1, GPIO.OUT)
servo1 = GPIO.PWM(servoPin1, 50)
servo1.start(0)

# 부저 설정
buz_PIN = 22
GPIO.setup(buz_PIN, GPIO.OUT)
p = GPIO.PWM(buz_PIN, 100)

# LED 설정
LED_COUNT = 8
GPIO_PIN = 21
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 100
LED_INVERT = False
LED_CHANNEL = 0
strip = PixelStrip(LED_COUNT, GPIO_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"format": 'RGB888', "size": (320, 320)})
picam2.configure(camera_config)
picam2.start()

chk = False
label=""
label_temp=""

# 모터 위치 설정 함수
def setServoPos1(degree):
    if degree > 180:
        degree = 180
    elif degree < 0:
        degree = 0

    duty = SERVO_MIN_DUTY + (degree * (SERVO_MAX_DUTY - SERVO_MIN_DUTY) / 180.0)
    GPIO.setup(servoPin1, GPIO.OUT)
    servo1.ChangeDutyCycle(duty)
    time.sleep(0.3)
    GPIO.setup(servoPin1, GPIO.IN)


# LED 제어 함수
def set_color(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


def clear_led(strip):
    set_color(strip, Color(0, 0, 0))


# 충격 감지 스레드
def vibLeft_thread():
    while True:
        time.sleep(0.01)
        global chk
        if GPIO.input(vibPinLeft) == CHECK_ON:
            print("Detection Left")
            setServoPos1(180)
            time.sleep(0.3)
            if chk:
                p.start(30)
                for _ in range(3):
                    set_color(strip, Color(255, 255, 255))
                    p.ChangeFrequency(392)
                    time.sleep(0.3)
                    clear_led(strip)
                    time.sleep(0.3)
                p.stop()


def vibRight_thread():
    while True:
        global chk
        time.sleep(0.01)
        if GPIO.input(vibPinRight) == CHECK_ON:
            print("Detection Right")
            setServoPos1(0)
            time.sleep(0.3)
            if chk:
                p.start(30)
                for _ in range(3):
                    set_color(strip, Color(255, 255, 255))
                    p.ChangeFrequency(392)
                    time.sleep(0.3)
                    clear_led(strip)
                    time.sleep(0.3)
                p.stop()


# 모델 경로 설정
model_path = 'pbest_edgetpu.tflite'
imgsz = 320

# 카메라 영상 스트리밍
async def generate_video_frames():
    global chk
    global label

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
                '''
                if label != label_temp:
                    label_temp = label
                '''
                if label == "Deer" or label == "Wildboar":
                    chk = True
                else:
                    chk = False

                if score >= 0.5:
                    bbox = detection_info['bbox']
                    x1, y1, x2, y2 = map(int, bbox)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label_text = f"{label} ({score:.2f})"
                    cv2.putText(frame, label_text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            except Exception as e:
                print(f"Error processing detection: {e}")

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        await asyncio.sleep(0.03)  # 약 20 FPS


@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_video_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/logs")
async def get_logs():
    global label_temp
    if label != label_temp:
        label_temp = label

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "message": "[Device:0]" + label + "Detected!!"
        }
        return JSONResponse(content=[log_data])
    else:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "message": "[Device:0] None Detected!!"
        }
        return JSONResponse(content=[log_data])





if __name__ == "__main__":
    sensorLeft_thread = threading.Thread(target=vibLeft_thread)
    sensorRight_thread = threading.Thread(target=vibRight_thread)

    sensorLeft_thread.start()
    sensorRight_thread.start()

    # FastAPI 서버 실행
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
