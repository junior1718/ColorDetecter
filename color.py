import numpy as np
import cv2

# настройки камеры
def gstreamer_pipeline(
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=30,
        flip_method=0,
):
    return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=true"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
    )


def process(frame):
    # размер квадрата
    rect_size = 100
    # диапазон значений для цвета + границы по hsv системе
    s_h = 255
    v_h = 255
    s_l = 50
    v_l = 50

    # настройка квадрата, флаг - переключение позиции квадрата
    width, height, channels = frame.shape
    if flag == 0:
        start_point = (int(height / 2 - rect_size / 2), int(width / 2 - rect_size / 2))
        end_point = (int(height / 2 + rect_size / 2), int(width / 2 + rect_size / 2))
    if flag == 1:
        start_point = (int(height / 4 - rect_size / 2), int(width / 4 - rect_size / 2))
        end_point = (int(height / 4 + rect_size / 2), int(width / 4 + rect_size / 2))
    if flag == 2:
        start_point = (int(height / 1.25 - rect_size / 2), int(width / 1.25 - rect_size / 2))
        end_point = (int(height / 1.25 + rect_size / 2), int(width / 1.25 + rect_size / 2))
    color = (255, 0, 0)
    thickness = 2
    rect = cv2.rectangle(frame, start_point, end_point, color, thickness)

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # настройка верхней и нижней границы для каждого цвета
    # yellow
    yellow_upper = np.array([40, s_h, v_h])
    yellow_lower = np.array([25, s_l, v_l])
    # green
    green_upper = np.array([70, s_h, v_h])
    green_lower = np.array([40, s_l, v_l])
    # cyan
    cyan_upper = np.array([105, s_h, v_h])
    cyan_lower = np.array([70, s_l, v_l])
    # blue
    blue_upper = np.array([130, s_h, v_h])
    blue_lower = np.array([105, s_l, v_l])
    # red1
    red1_upper = np.array([10, s_h, v_h])
    red1_lower = np.array([0, s_l, v_l])
    # red2
    red2_upper = np.array([180, s_h, v_h])
    red2_lower = np.array([160, s_l, v_l])
    # purple
    purple_upper = np.array([160, s_h, v_h])
    purple_lower = np.array([130, s_l, v_l])
    # orange
    orange_upper = np.array([25, s_h, v_h])
    orange_lower = np.array([10, s_l, v_l])

    # считываем кадр для обработки
    mask_frame = hsv_frame[start_point[1]:end_point[1] + 1, start_point[0]:end_point[0] + 1]

    # маска цвета - берём фрагмент и смотрим на нём цвета из диапазона
    mask_blue = cv2.inRange(mask_frame, blue_lower, blue_upper)
    mask_green = cv2.inRange(mask_frame, green_lower, green_upper)
    mask_yellow = cv2.inRange(mask_frame, yellow_lower, yellow_upper)
    mask_cyan = cv2.inRange(mask_frame, cyan_lower, cyan_upper)
    mask_red1 = cv2.inRange(mask_frame, red1_lower, red1_upper)
    mask_red2 = cv2.inRange(mask_frame, red2_lower, red2_upper)
    mask_purple = cv2.inRange(mask_frame, purple_lower, purple_upper)
    mask_orange = cv2.inRange(mask_frame, orange_lower, orange_upper)

    # считаем ненулевые значения
    blue_rate = np.count_nonzero(mask_blue) / (rect_size * rect_size)
    green_rate = np.count_nonzero(mask_green) / (rect_size * rect_size)
    yellow_rate = np.count_nonzero(mask_yellow) / (rect_size * rect_size)
    cyan_rate = np.count_nonzero(mask_cyan) / (rect_size * rect_size)
    red1_rate = np.count_nonzero(mask_red1) / (rect_size * rect_size)
    red2_rate = np.count_nonzero(mask_red2) / (rect_size * rect_size)
    purple_rate = np.count_nonzero(mask_purple) / (rect_size * rect_size)
    orange_rate = np.count_nonzero(mask_orange) / (rect_size * rect_size)

    # настройки вывода текста, результата
    org = end_point
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.7

    # массив с цветами и их строковым представлением
    color_rates_names = [(blue_rate, ' blue '), (green_rate, ' green '), (yellow_rate, ' yellow '),
                         (cyan_rate, ' cyan '), (red1_rate + red2_rate, ' red '), (purple_rate, ' purple '),
                         (orange_rate, ' orange ')]

    # считаем максимальный цвет и выводим, если его достаточно (значение больше 0.7)
    max_color = max(color_rates_names)
    if max_color[0] > 0.7:
        text = cv2.putText(rect, max_color[1], org, font, fontScale, color, thickness, cv2.LINE_AA)
    else:
        text = cv2.putText(rect, ' not detected ', org, font, fontScale, color, thickness, cv2.LINE_AA)


    # вывод инфы о том, какие значения в квадрате
    av_hue = np.average(mask_frame[:, :, 0])
    av_sat = np.average(mask_frame[:, :, 1])
    av_val = np.average(mask_frame[:, :, 2])
    average = [int(av_hue), int(av_sat), int(av_val)]

    # вывод нужного цвета
    text = cv2.putText(rect, str(average) + "blue: " + str(blue_rate), (10, 50), font, fontScale, color, thickness,
                       cv2.LINE_AA)
    cv2.putText(rect, "green: " + str(green_rate), (10, 100), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(rect, "yellow: " + str(yellow_rate), (10, 150), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(rect, "cyan: " + str(cyan_rate), (10, 200), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(rect, "red: " + str(red1_rate + red2_rate), (10, 250), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(rect, "purple: " + str(purple_rate), (10, 300), font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.putText(rect, "orange: " + str(orange_rate), (10, 350), font, fontScale, color, thickness, cv2.LINE_AA)

    frame = text
    return frame


print('Press 4 to Quit the Application, Press 5 to Switch rectangle position\n')

# Open Default Camera вместо 0
cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=4), cv2.CAP_GSTREAMER)  # gstreamer_pipeline(flip_method=4), cv2.CAP_GSTREAMER)

flag = 0

# флаг отвечает за номер квадрата. На 5 переключение, на 4 закрытие программы
while (cap.isOpened()):
    # Take each Frame
    ret, frame = cap.read()

    # Flip Video vertically (180 Degrees)
    frame = cv2.flip(frame, 180)

    invert = process(frame)

    # Show video
    cv2.imshow('Cam', frame)

    # Exit if "4" is pressed
    k = cv2.waitKey(1) & 0xFF
    if k == 53:  # ord 5 (I hope)
        # Switch
        flag = (flag + 1) % 3
        print(flag)
    if k == 52:  # ord 4
        # Quit
        print('Good Bye!')
        break

# Release the Cap and Video
cap.release()
cv2.destroyAllWindows()
