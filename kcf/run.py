# -*-coding:utf-8-*-
import cv2
from tracker import KCFTracker


selection = None
track_window = None
drag_start = None


def draw_military_lock(img, x, y, w, h, showLocked=False, color=None):
    # color = (0, 0, 255)
    # 根据w和h的最小值来计算角线的长度和字体大小
    min_size = min(w, h)
    corner_length = max(int(min_size * 0.1), 10)  # 角线长度至少为10
    font_scale = max(min_size / 200, 0.5)  # 字体大小至少为0.7

    # 左上角
    cv2.line(img, (x, y), (x + corner_length, y), color, 2)
    cv2.line(img, (x, y), (x, y + corner_length), color, 2)
    # 右上角
    cv2.line(img, (x + w, y), (x + w - corner_length, y), color, 2)
    cv2.line(img, (x + w, y), (x + w, y + corner_length), color, 2)
    # 左下角
    cv2.line(img, (x, y + h), (x + corner_length, y + h), color, 2)
    cv2.line(img, (x, y + h), (x, y + h - corner_length), color, 2)
    # 右下角
    cv2.line(img, (x + w, y + h), (x + w - corner_length, y + h), color, 2)
    cv2.line(img, (x + w, y + h), (x + w, y + h - corner_length), color, 2)

    # 根据计算的字体大小绘制文本
    if showLocked:
        cv2.putText(img, "LOCKED", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 2)


# 鼠标选框（做目标跟踪框）
def onmouse(event, x, y, flags, param):
    global selection, track_window, drag_start
    if event == cv2.EVENT_LBUTTONDOWN:
        drag_start = (x, y)
        track_window = None
    if drag_start:
        xmin = min(x, drag_start[0])
        ymin = min(y, drag_start[1])
        xmax = max(x, drag_start[0])
        ymax = max(y, drag_start[1])
        selection = (xmin, ymin, xmax, ymax)
    if event == cv2.EVENT_LBUTTONUP:
        drag_start = None
        track_window = selection
        selection = None


def tracker(cam, frame, bbox):
    tracker = KCFTracker(True, True, True) # (hog, fixed_Window, multi_scale)
    tracker.init(bbox, frame)
    
    while True:
        ok, frame = cam.read()

        timer = cv2.getTickCount()
        bbox = tracker.update(frame)
        bbox = list(map(int, bbox))
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        # Tracking success
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        # cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        draw_military_lock(frame, p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
        print("左上角坐标为",p1,"右下角坐标为",p2)
        # Put FPS
        cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

        cv2.imshow("image", frame)

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    # cam.release()
    # cv2.destroyAllWindows()

def airtrack():
    global selection, track_window, drag_start
    
    exact_track_window = ()
    cv2.namedWindow('image', 1)
    cv2.setMouseCallback('image', onmouse)

    flag = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Read Frame Error!")
            break
        # print("Processing Frame {}".format(flag))
        img_raw = frame  # cv2.imread(f)
        image = img_raw.copy()

        # We need to initialize the tracker on the first frame
        if flag == 0:
            # Start a track on the object you want. box the object using the mouse and press 'Enter' to start tracking
            while True:
                ret, image = cap.read()
                img_first = image.copy()

                if track_window: # 框选动作完成
                    cv2.rectangle(img_first, (track_window[0], track_window[1]), (track_window[2], track_window[3]), (0, 0, 255), 1)
                elif selection: # 处于正在框选区域的状态
                    cv2.rectangle(img_first, (selection[0], selection[1]), (selection[2], selection[3]), (0, 0, 255), 1)

                if exact_track_window:
                    cv2.rectangle(img_first, (exact_track_window[0], exact_track_window[1]), (exact_track_window[2], exact_track_window[3]), (0, 255, 255), 1)

                cv2.imshow('image', img_first)

                if cv2.waitKey(10) == 32:  # 判断是否为空格键，是则将框选的区域赋值给exact_track_window，并设置k=2，开始跟踪
                    exact_track_window = list(track_window)
                    exact_track_window[2] = exact_track_window[2] - exact_track_window[0]
                    exact_track_window[3] = exact_track_window[3] - exact_track_window[1]
                    exact_track_window = tuple(exact_track_window)
                    flag = 2
                    # tracker1.init(image, exact_track_window)
                    break

                # Exit if ESC pressed
                if (cv2.waitKey(10) & 0xff) == 27:
                    break
        else:
            tracker(cap, frame, exact_track_window)
            track_window = None
            exact_track_window = None
            flag = 0

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # cap = cv2.VideoCapture("../../air.mp4")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open video source!")
        exit(-1)

    airtrack()