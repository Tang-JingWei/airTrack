# This Python file uses the following encoding: utf-8
import sys
import cv2
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen

sys.path.append(r'./kcf')
import kcf.tracker
import kcf.fhog
import kcf.run

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

        self.cap = cv2.VideoCapture(0)
        self.kcf_image = None
        self.timer = QtCore.QTimer(self)
        self.timer.start(10)

        self.ui.imageLabel.start_pos = None
        self.ui.imageLabel.end_pos = None

        # 为 imageLabel 绑定鼠标事件
        self.ui.imageLabel.mousePressEvent = self.monitor_mousePressEvent
        self.ui.imageLabel.mouseMoveEvent = self.monitor_mouseMoveEvent
        self.ui.imageLabel.mouseReleaseEvent = self.monitor_mouseReleaseEvent
        # self.ui.imageLabel.paintEvent = self.imageLabel_paintEvent  # 添加 paintEvent 处理

        self.selection = None
        self.track_flag = False
        self.tracker = None  # (hog, fixed_Window, multi_scale)
        self.track_window = None
        self.tracker_initialized = False

        self.init_slot()

    def init_slot(self):
        # 开始绑定信号和槽
        self.timer.timeout.connect(self.showimg)
        self.ui.trackButton.clicked.connect(self.track_confirm)

    def monitor_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("单击: ", event.pos(), end='', flush=True)
            if self.track_flag == False:
                self.ui.imageLabel.start_pos = event.pos()
                self.ui.imageLabel.end_pos = event.pos()

                self.track_window = None

    def monitor_mouseMoveEvent(self, event):
        if self.ui.imageLabel.start_pos is not None:
            if self.track_flag == False:
                self.ui.imageLabel.end_pos = event.pos()

                xmin = min(self.ui.imageLabel.start_pos.x(), self.ui.imageLabel.end_pos.x())
                ymin = min(self.ui.imageLabel.start_pos.y(), self.ui.imageLabel.end_pos.y())
                xmax = max(self.ui.imageLabel.start_pos.x(), self.ui.imageLabel.end_pos.x())
                ymax = max(self.ui.imageLabel.start_pos.y(), self.ui.imageLabel.end_pos.y())
                self.selection = (xmin, ymin, xmax, ymax)

    def monitor_mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.track_flag == False:
                self.track_window = self.selection
                print("track_window:", self.track_window)
                self.ui.imageLabel.start_pos = None
                self.selection = None

    def track_confirm(self):
        if self.track_flag == True:
            self.track_flag = False
            self.track_window = None
            self.selection = None
            self.tracker_initialized = False
            self.ui.trackButton.setText("锁定")
            # 设置按钮背景色为默认
            self.ui.trackButton.setStyleSheet("")
        elif self.track_flag == False:
            self.track_flag = True
            self.ui.trackButton.setText("取消锁定")
            # 设置按钮背景色为红色
            self.ui.trackButton.setStyleSheet("background-color: red;")

    # QT显示图片函数
    def showimg(self):
        ret, frame = self.cap.read()

        if ret:
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.flip(frame, 1)

            # KCF
            if self.track_flag == True:
                if self.track_window is not None:
                    if self.tracker_initialized == False:
                        exact_track_window = list(self.track_window)
                        exact_track_window[2] = exact_track_window[2] - exact_track_window[0]
                        exact_track_window[3] = exact_track_window[3] - exact_track_window[1]
                        exact_track_window = tuple(exact_track_window)

                        self.tracker = kcf.tracker.KCFTracker(True, True, True) 
                        self.tracker.init(exact_track_window, frame)
                        self.tracker_initialized = True

                    try:
                        bbox = self.tracker.update(frame)
                        bbox = list(map(int, bbox))

                        # Tracking success
                        p1 = (int(bbox[0]), int(bbox[1]))
                        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                        # cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                        kcf.run.draw_military_lock(frame, p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
                        print(f"目标锁定：\r左上角坐标为 {p1} 右下角坐标为 {p2}", end='', flush=True)
                    except:
                        self.tracker_initialized = False
                        self.track_window = None
                    
            elif self.track_flag == False:
                if self.track_window is not None:
                    cv2.rectangle(frame, (self.track_window[0], self.track_window[1]),
                                (self.track_window[2], self.track_window[3]), (0, 255, 255), 2) # 黄色
                elif self.selection is not None:
                    cv2.rectangle(frame, (self.selection[0], self.selection[1]),
                                (self.selection[2], self.selection[3]), (0, 255, 0), 2) # 绿色

            im = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[2] * frame.shape[1],
                        QImage.Format_BGR888)
            self.ui.imageLabel.setPixmap(QPixmap.fromImage(im))
        # 否则报错
        else:
            print("摄像头读取错误, 退出程序")
            exit(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())

