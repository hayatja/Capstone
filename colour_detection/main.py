import detect_border
import keyboard
import cv2

if __name__ == "__main__":
    videoCaptureObject = cv2.VideoCapture(0)

    while True:
        try:
            if keyboard.is_pressed('q'):
                break
            elif keyboard.is_pressed('c'):
                print(detect_border.check(videoCaptureObject))

        except Exception as e:
            print(e)

# python .\main.py