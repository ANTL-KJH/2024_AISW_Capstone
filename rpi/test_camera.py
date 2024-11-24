import cv2

# 라즈베리파이 카메라 초기화
camera = cv2.VideoCapture(0)  # '0'은 기본 카메라 장치를 의미

if not camera.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

print("카메라가 성공적으로 열렸습니다. ESC 키를 눌러 종료하세요.")

while True:
    # 프레임 읽기
    ret, frame = camera.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # 프레임 표시
    cv2.imshow('Raspberry Pi Camera Test', frame)

    # ESC 키를 누르면 종료
    key = cv2.waitKey(1)
    if key == 27:  # ESC 키 코드
        print("프로그램 종료")
        break

# 카메라 자원 해제
camera.release()
cv2.destroyAllWindows()
