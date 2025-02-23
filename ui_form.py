# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1023, 675)
        self.author = QAction(MainWindow)
        self.author.setObjectName(u"author")
        self.version = QAction(MainWindow)
        self.version.setObjectName(u"version")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.trackButton = QPushButton(self.centralwidget)
        self.trackButton.setObjectName(u"trackButton")
        self.trackButton.setGeometry(QRect(10, 510, 161, 71))
        font = QFont()
        font.setPointSize(20)
        self.trackButton.setFont(font)
        self.imageLabel = QLabel(self.centralwidget)
        self.imageLabel.setObjectName(u"imageLabel")
        self.imageLabel.setGeometry(QRect(10, 10, 640, 480))
        font1 = QFont()
        font1.setPointSize(24)
        self.imageLabel.setFont(font1)
        self.imageLabel.setTextFormat(Qt.RichText)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1023, 34))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.author)
        self.menu.addAction(self.version)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.author.setText(QCoreApplication.translate("MainWindow", u"\u4f5c\u8005", None))
        self.version.setText(QCoreApplication.translate("MainWindow", u"\u7248\u672c", None))
        self.trackButton.setText(QCoreApplication.translate("MainWindow", u"\u9501\u5b9a", None))
        self.imageLabel.setText(QCoreApplication.translate("MainWindow", u"\u5b9e\u65f6\u753b\u9762", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e", None))
    # retranslateUi

