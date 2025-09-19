from email.mime import image
import cv2
import sys
import json
import numpy as np
from functools import partial

CONFIG_FILE = "LAB-cal.json"
WINDOW_NAME = "LAB Filter"
TB_L_MIN = "L Min"
TB_L_MAX = "L Max"
TB_A_MIN = "A Min"
TB_A_MAX = "A Max"
TB_B_MIN = "B Min"
TB_B_MAX = "B Max"

# Initial color range values
l_min = 0
a_min = 0
b_min = 0
l_max = 255
a_max = 255
b_max = 255


def update_color_value(x, color, is_min):
    global l_min, a_min, b_min, l_max, a_max, b_max
    match color:
        case "L":
            if is_min:
                l_min = x
            else:
                l_max = x
        case "A":
            if is_min:
                a_min = x
            else:
                a_max = x
        case "B":
            if is_min:
                b_min = x
            else:
                b_max = x
        case _:
            pass


def load_config(config_path):
    # TODO: LAB-cal.json 파일을 읽어와서 전역 변수에 설정하기
    global l_min, l_max, a_min, a_max, b_min, b_max

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        l_min = int(data.get("l_min", l_min))
        l_max = int(data.get("l_max", l_max))
        a_min = int(data.get("a_min", a_min))
        a_max = int(data.get("a_max", a_max))
        b_min = int(data.get("b_min", b_min))
        b_max = int(data.get("b_max", b_max))
    except FileNotFoundError:
        print(f"config file not found: {config_path}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")


def save_config(config_path):
    # TODO: 현재 설정된 전역 변수를 LAB-cal.json 파일로 저장하기
    save_data = {
        # TODO: Fill out with l_min, l_max, a_min, a_max, b_min, b_man, values respectively.
        "l_min": l_min,
        "l_max": l_max,
        "a_min": a_min,
        "a_max": a_max,
        "b_min": b_min,
        "b_max": b_max
    }    
    with open(config_path, "w") as f:
        json.dump(save_data, f, indent=4)    
    pass


def update_trackbar_positions():
    cv2.setTrackbarPos(TB_L_MIN, WINDOW_NAME, l_min)
    cv2.setTrackbarPos(TB_L_MAX, WINDOW_NAME, l_max)
    cv2.setTrackbarPos(TB_A_MIN, WINDOW_NAME, a_min)
    cv2.setTrackbarPos(TB_A_MAX, WINDOW_NAME, a_max)
    cv2.setTrackbarPos(TB_B_MIN, WINDOW_NAME, b_min)
    cv2.setTrackbarPos(TB_B_MAX, WINDOW_NAME, b_max)


def find_biggest_contour(mask):
    # TODO: mask 변수 값으로 부터 연결된 객체 중 가장 큰 객체 찾기
    contour, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contour:
        biggest = max(contour, key=cv2.contourArea)
    else:
        return None
    return biggest



def draw_boundingbox(image, contour):
    # TODO: 가장 큰 객체에 대해 외접하는 바운딩 박스 그리기, cv2.boundingRect() 사용
    for cnt in contour:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    # TODO: Rect: (x y w h) 형태로 좌표 출력, cv2.putText() 사용
    cv2.putText(image, f"x: {x}, y:{y}, {w}, {h}",
                org=(x, y), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=2,
                color=(0, 255, 0),
                thickness=3,
                lineType=cv2.LINE_AA
                )
    pass


if __name__ == "__main__":
    # Trackbar UI
    cv2.namedWindow(WINDOW_NAME)
    cv2.resizeWindow(WINDOW_NAME, 800, 200)
    cv2.createTrackbar(TB_L_MIN, WINDOW_NAME, l_min, 255,
                       partial(update_color_value, color="L", is_min=True))
    cv2.createTrackbar(TB_L_MAX, WINDOW_NAME, l_max, 255,
                       partial(update_color_value, color="L", is_min=False))
    cv2.createTrackbar(TB_A_MIN, WINDOW_NAME, a_min, 255,
                       partial(update_color_value, color="A", is_min=True))
    cv2.createTrackbar(TB_A_MAX, WINDOW_NAME, a_max, 255,
                       partial(update_color_value, color="A", is_min=False))
    cv2.createTrackbar(TB_B_MIN, WINDOW_NAME, b_min, 255,
                       partial(update_color_value, color="B", is_min=True))
    cv2.createTrackbar(TB_B_MAX, WINDOW_NAME, b_max, 255,
                       partial(update_color_value, color="B", is_min=False))

    # Load if config file is given
    if len(sys.argv) > 1:
        load_config(sys.argv[1])

        # Update trackbar positions
        update_trackbar_positions()

        print(f"Loaded config:")
        print(f"L : {l_min} - {l_max}")
        print(f"A : {a_min} - {a_max}")
        print(f"B : {b_min} - {b_max}")

    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        if ret is False:
            break

        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        # Filter in BGR space (OpenCV uses BGR)
        lower = np.array([l_min, a_min, b_min])
        upper = np.array([l_max, a_max, b_max])
        mask = cv2.inRange(lab, lower, upper)
        masked_img = cv2.bitwise_and(img, img, mask=mask)

        # IMPLEMENT ME!
        # mask 변수 값으로 부터 연결된 객체 중 가장 큰 객체 찾기
        biggest_contour = find_biggest_contour(mask)  # Implement this function

        # 가장 큰 객체에 대해 외접하는 바운딩 박스 그리기, cv2.boundingRect() 사용
        draw_boundingbox(masked_img, biggest_contour)

        # Show filtered result
        combined = np.hstack((img, masked_img))
        cv2.imshow("LAB Filter Result", cv2.resize(combined, (1280, 600)))

        # Exit on ESC key press
        key = cv2.waitKey(1) & 0xff
        match key:
            case 27:
                break
            case 115:  # 's' key
                # Save current filter settings
                save_data = {
                    "l_min": l_min, "l_max": l_max,
                    "a_min": a_min, "a_max": a_max,
                    "b_min": b_min, "b_max": b_max
                }
                save_config(CONFIG_FILE)
                print(f"File saved to {CONFIG_FILE}")
            case _:
                pass

    cap.release()
    cv2.destroyAllWindows()
