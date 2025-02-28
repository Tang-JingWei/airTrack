#!/usr/bin/python3
import sys
from os.path import abspath, join, dirname
sys.path.insert(0, join(abspath(dirname(__file__))))

import cv2
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QIcon

import os

import kcf.tracker
import kcf.run

from enum import Enum

class MOVEMISSON(Enum):
    NONE_MOVE = 0
    CLICK_MOVE = 1
    TRACK_MOVE = 2

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py

from ui_form import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.cap = cv2.VideoCapture("video/car.mp4")
        self.cap_width = 640
        self.cap_height = 360
        self.fps = 0
        self.timer = QtCore.QTimer(self)
        self.timer.start(20)

        # 为 imageLabel 绑定鼠标事件
        self.ui.imageLabel.mousePressEvent = self.monitor_mousePressEvent
        self.ui.imageLabel.mouseMoveEvent = self.monitor_mouseMoveEvent
        self.ui.imageLabel.mouseReleaseEvent = self.monitor_mouseReleaseEvent
        self.ui.imageLabel.wheelEvent = self.monitor_mouseWheelEvent

        # 定时器用于监测 track_window 是否为空
        self.track_window_timer = QtCore.QTimer(self)
        self.track_window_timer.timeout.connect(self.check_track_window)
        self.track_window_timer.start(200)

        self.debug_draw = False # 调试绘制控制
        self.ui.imageLabel.start_pos = None
        self.ui.imageLabel.end_pos = None
        self.selection = None
        self.mouse_clicked = None  # 记录点击点
        self.click_window_size = 15  # 漫游窗口大小 默认值
        self.mission_flag = MOVEMISSON.NONE_MOVE  # 追踪状态置位
        self.tracker = None  # (hog, fixed_Window, multi_scale)
        self.track_window = None
        self.mission_initialized = False

        # 滚轮控制绘制中心的框
        self.show_wheel_box = False  # 标志位，用于控制是否显示中间的框
        self.show_wheel_timer = QtCore.QTimer(self)  # 定时器，用于控制框的显示时间
        self.show_wheel_timer.timeout.connect(self.hide_wheel_box)

        self.init_slot()

    def init_slot(self):
        # 开始绑定信号和槽
        self.timer.timeout.connect(self.showimg)
        self.ui.trackButton.clicked.connect(self.track_confirm)
        self.ui.clickButton.clicked.connect(self.click_confirm)

    # 定时检查 track_window 并控制追踪按钮启用禁用(在 NONE_MOVE 状态下)
    def check_track_window(self):
        if self.mission_flag == MOVEMISSON.NONE_MOVE:
            if self.track_window is None:
                self.ui.trackButton.setEnabled(False)
            else:
                self.ui.trackButton.setEnabled(True)

    # 隐藏中间的框
    def hide_wheel_box(self):
        self.show_wheel_box = False  # 定时器超时后，设置标志位为 False，隐藏中间的框
        self.show_wheel_timer.stop()  # 停止定时器

    # [左键点击]
    def monitor_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # print("单击: ", event.pos(), end='', flush=True)
            if self.mission_flag == MOVEMISSON.NONE_MOVE:
                self.ui.imageLabel.start_pos = event.position().toPoint()
                self.ui.imageLabel.end_pos = event.position().toPoint()

                self.track_window = None
            elif self.mission_flag == MOVEMISSON.CLICK_MOVE: # 漫游状态
                self.mouse_clicked = event.position().toPoint()

    # [左键移动]
    def monitor_mouseMoveEvent(self, event):
        if self.ui.imageLabel.start_pos is not None:
            if self.mission_flag == MOVEMISSON.NONE_MOVE:
                self.ui.imageLabel.end_pos = event.position().toPoint()

                xmin = min(self.ui.imageLabel.start_pos.x(), self.ui.imageLabel.end_pos.x())
                ymin = min(self.ui.imageLabel.start_pos.y(), self.ui.imageLabel.end_pos.y())
                xmax = max(self.ui.imageLabel.start_pos.x(), self.ui.imageLabel.end_pos.x())
                ymax = max(self.ui.imageLabel.start_pos.y(), self.ui.imageLabel.end_pos.y())
                self.selection = (xmin, ymin, xmax, ymax)
            elif self.mission_flag == MOVEMISSON.CLICK_MOVE: # 漫游状态
                self.mouse_clicked = None

    # [左键释放]
    def monitor_mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mission_flag == MOVEMISSON.NONE_MOVE:
                self.track_window = self.selection
                # print("track_window:", self.track_window)
                self.ui.imageLabel.start_pos = None
                self.selection = None
                self.mission_initialized = False # 凡是鼠标左键释放都要重新初始化追踪器
            elif self.mission_flag == MOVEMISSON.CLICK_MOVE: # 漫游状态
                if self.mouse_clicked is not None:
                    x = self.mouse_clicked.x()
                    y = self.mouse_clicked.y()
                    size = self.click_window_size
                    self.track_window = (x - size, y - size, x + size, y + size)
                    self.mouse_clicked = None
                    self.mission_initialized = False # 凡是鼠标左键释放都要重新初始化追踪器

    # [滚轮滚动]
    def monitor_mouseWheelEvent(self, event):
        if self.mission_flag == MOVEMISSON.CLICK_MOVE:
            # 获取滚轮滚动的方向
            delta = event.angleDelta().y()
            if delta > 0:
                # 向上滚动，增大 size
                self.click_window_size = min(self.click_window_size + 5, 100)  # 限制最大 size 为 100
            else:
                # 向下滚动，减小 size
                self.click_window_size = max(self.click_window_size - 5, 10)  # 限制最小 size 为 10
        
        self.show_wheel_box = True  # 滚轮滚动后，设置标志位为 True，显示中间的框
        self.show_wheel_timer.start(500)  # 启动定时器，1 秒后隐藏框

    # 追踪按钮响应函数
    def track_confirm(self):
        if self.mission_flag == MOVEMISSON.TRACK_MOVE:
            self.mission_flag = MOVEMISSON.NONE_MOVE
            self.track_window = None
            self.selection = None
            self.ui.trackButton.setText("锁定")
            # 设置按钮背景色为默认
            self.ui.trackButton.setStyleSheet("")
            self.ui.clickButton.setEnabled(True) # 启用漫游按钮
        elif self.mission_flag == MOVEMISSON.NONE_MOVE:
            self.mission_flag = MOVEMISSON.TRACK_MOVE
            self.ui.trackButton.setText("取消锁定")
            # 设置按钮背景色为红色
            self.ui.trackButton.setStyleSheet("background-color: red;")
            self.ui.clickButton.setEnabled(False) # 禁用漫游按钮

    # click 确认追踪
    def click_confirm(self):
        if self.mission_flag == MOVEMISSON.CLICK_MOVE:
            self.mission_flag = MOVEMISSON.NONE_MOVE
            self.track_window = None
            self.ui.clickButton.setText("漫游")
            # 设置按钮背景色为默认
            self.ui.clickButton.setStyleSheet("")
            self.ui.trackButton.setEnabled(True) # 启用锁定按钮
        elif self.mission_flag == MOVEMISSON.NONE_MOVE:
            self.mission_flag = MOVEMISSON.CLICK_MOVE
            self.ui.clickButton.setText("取消漫游")
            # 设置按钮背景色为红色
            self.ui.clickButton.setStyleSheet("background-color: red;")
            self.ui.trackButton.setEnabled(False) # 禁用锁定按钮

    # QT显示图片函数
    def showimg(self):
        ret, frame = self.cap.read()

        if ret:
            print(frame.shape)
            start = cv2.getTickCount()

            frame = cv2.resize(frame, (self.cap_width, self.cap_height))
            frame = cv2.flip(frame, 1)

            # 开启KCF追踪 TRACK_MOVE 状态 | CLICK_MOVE 状态
            if (self.mission_flag == MOVEMISSON.TRACK_MOVE) or (self.mission_flag == MOVEMISSON.CLICK_MOVE):
                if self.track_window is not None:
                    if self.mission_initialized == False:
                        exact_track_window = list(self.track_window)
                        exact_track_window[2] = exact_track_window[2] - exact_track_window[0]
                        exact_track_window[3] = exact_track_window[3] - exact_track_window[1]
                        exact_track_window = tuple(exact_track_window)

                        self.tracker = kcf.tracker.KCFTracker(True, True, True) 
                        self.tracker.init(exact_track_window, frame)
                        self.mission_initialized = True

                    try:
                        bbox = self.tracker.update(frame)
                        bbox = list(map(int, bbox))

                        # Tracking success
                        p1 = (int(bbox[0]), int(bbox[1]))
                        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                        # cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                        kcf.run.draw_military_lock(frame, p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1], False, (0, 0, 255))
                        # print(f"目标锁定：\r左上角坐标为 {p1} 右下角坐标为 {p2}", end='', flush=True)
                    except Exception as e:
                        print(e)
                        self.mission_initialized = False
                        self.track_window = None

            # NONE_MOVE 状态 
            if (self.mission_flag == MOVEMISSON.NONE_MOVE) or (self.debug_draw == True):
                if self.track_window is not None:
                    cv2.rectangle(frame, (self.track_window[0], self.track_window[1]),
                                (self.track_window[2], self.track_window[3]), (0, 255, 255), 2) # 黄色
                elif self.selection is not None:
                    cv2.rectangle(frame, (self.selection[0], self.selection[1]),
                                (self.selection[2], self.selection[3]), (0, 255, 0), 2) # 绿色

            if self.mission_flag == MOVEMISSON.CLICK_MOVE:
                # 绘制中间的框
                if self.show_wheel_box:
                    center_x = self.cap_width // 2
                    center_y = self.cap_height // 2
                    p1 = (center_x - self.click_window_size, center_y - self.click_window_size)
                    p2 = (center_x + self.click_window_size, center_y + self.click_window_size)
                    kcf.run.draw_military_lock(frame, p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1], False, (0, 0, 255))
                    # cv2.rectangle(frame, p1, p2, (255, 0, 0), 2)

            self.fps = cv2.getTickFrequency() / (cv2.getTickCount() - start)

            # 打印追踪目标信息
            # print(f"\rdetect_flag, cx, cy, dx, dy: {self.target.detect_flag}, {self.target.cx}, {self.target.cy}, {self.target.dx}, {self.target.dy}", end='', flush=True)

            # 画面添加额外信息
            # 帧率
            cv2.putText(frame, "FPS: " + ("99+" if self.fps > 99 else str(int(self.fps))), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 170, 50), 1)
            cross_length = 20
            # 十字线
            cv2.line(frame, (int(self.cap_width / 2) - cross_length, int(self.cap_height / 2)), (int(self.cap_width / 2) + cross_length, int(self.cap_height / 2)), (0, 255, 0), 1)
            cv2.line(frame, (int(self.cap_width / 2), int(self.cap_height / 2) - cross_length), (int(self.cap_width / 2), int(self.cap_height / 2) + cross_length), (0, 255, 0), 1)

            # 显示最终图片
            im = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[2] * frame.shape[1],
                        QImage.Format_BGR888)
            self.ui.imageLabel.setPixmap(QPixmap.fromImage(im))
        # 否则报错
        else:
            print("摄像头读取错误, 退出程序")
            exit(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon("pic/logo.png"))
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())

