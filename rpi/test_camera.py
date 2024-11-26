from picamera2 import Picamera2
import cv2

#uvicorn camera:app --host 0.0.0.0 --port 8000
#python -m unicorn camera:app --host 0.0.0.0 --port 8000
# Picamera2 객체 생성
picam2 = Picamera2()

# 카메라 구성 설정
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)

# 카메라 시작
picam2.start()

print("카메라가 실행 중입니다. ESC 키를 눌러 종료하세요.")

try:
    while True:
        # 프레임 캡처
        frame = picam2.capture_array()

        # OpenCV로 프레임 표시
        cv2.imshow("Raspberry Pi Camera Test", frame)

        # ESC 키로 종료
        if cv2.waitKey(1) & 0xFF == 27:  # ESC 키
            print("프로그램 종료")
            break
finally:
    # 카메라 종료 및 자원 해제
    picam2.stop()
    cv2.destroyAllWindows()
