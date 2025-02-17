#!/usr/bin/env python
"""
afk.py
AFK锁屏脚本
2025.2.13
"""
import subprocess
import sys
from datetime import datetime, timedelta

from PyQt5.QtCore import QTimer, QElapsedTimer, Qt, QTime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout


class StandbyApp(QWidget):
    def __init__(self,password):
        self.time_up=False
        self.password = password
        self.normal_mode = True
        super().__init__()
        self.initUI()
        self.initTimer()
        self.grabMouse()  # 捕获鼠标 防止逃逸!!!

    def initUI(self):
        self.setWindowTitle('待机')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.title_label = QLabel('待机程序 密码看条码', self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont('Arial', 80))

        self.time_label = QLabel('已挂机00:00:00', self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont('Arial', 60))

        self.user_label = QLabel(f"{subprocess.getoutput('whoami')}正在挂机".title(), self)
        self.user_label.setAlignment(Qt.AlignCenter)
        self.user_label.setFont(QFont('Arial', 40))

        self.pwd_input = QLineEdit(self)
        self.pwd_input.setPlaceholderText('输入密码返回桌面')
        self.pwd_input.setFont(QFont('Arial', 24))
        self.pwd_input.setMaximumWidth(400)
        self.pwd_input.returnPressed.connect(self.check_password)

        # 添加当前时间的显示标签
        self.current_time_label = QLabel('当前时间: 00:00:00', self)
        self.current_time_label.setAlignment(Qt.AlignCenter)
        self.current_time_label.setFont(QFont('Arial', 40))

        vbox = QVBoxLayout()
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.title_label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.time_label)
        hbox1.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addStretch(1)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.user_label)
        hbox2.addStretch(1)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)

        # 将当前时间标签添加到布局
        hbox3 = QHBoxLayout()
        hbox3.addStretch(1)
        hbox3.addWidget(self.current_time_label)
        hbox3.addStretch(1)
        vbox.addLayout(hbox3)
        vbox.addStretch(1)

        hbox4 = QHBoxLayout()
        hbox4.addStretch(1)
        hbox4.addWidget(self.pwd_input)
        hbox4.addStretch(1)
        vbox.addLayout(hbox4)
        vbox.addStretch(1)

        self.setLayout(vbox)
        self.pwd_input.setFocus()

    def getTime(self):
        """修复跨天判断的核心函数"""
        # 获取基准日期（根据当前时间动态调整）
        current = datetime.now()
        base_date=current.date()
        if 0 <= current.hour < 5:
            base_date -= timedelta(days=1)  # 回溯到前一天

        # 构建正确的时间区间
        start = datetime.combine(base_date, datetime.strptime("22:30", "%H:%M").time())
        end = datetime.combine(base_date + timedelta(days=1), datetime.strptime("05:30", "%H:%M").time())

        if start <= current < end:
            #print('time is up')
            self.time_up = True
            #start_time += timedelta(days=1)

    def initTimer(self):
        self.timer = QTimer(self)
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.timer.timeout.connect(self.update_time)
        self.timer.timeout.connect(self.update_current_time)  # 添加更新当前时间的方法
        self.timer.start(1000)  # 每秒更新一次

    def update_time(self):
        elapsed = self.elapsed_timer.elapsed()
        seconds = elapsed // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if not self.normal_mode:
            if self.password == 'rest':
                self.time_label.setText(f"不限时挂机状态")
            else:
                self.time_label.setText(f"自动挂机 早上5:30自动关闭")
        else:
            self.time_label.setText(f"已挂机{hours:02}:{minutes:02}:{seconds:02}")

    def update_current_time(self):
        current_time = QTime.currentTime()
        formatted_time = current_time.toString('hh:mm:ss')  # 格式化当前时间
        self.current_time_label.setText(f"当前时间: {formatted_time}")
        #self.getTime((22,5),(30,30),(0,0))
        self.getTime()
        if self.time_up or self.password == 'rest':
            self.title_label.setText('休息时间 自动待机')
            self.normal_mode = False
            self.pwd_input.setPlaceholderText('退出功能停用')
            self.pwd_input.setEnabled(False)  # 停止密码输入
        else:
            self.title_label.setText('待机程序 密码看条码')
            self.normal_mode = True
            self.pwd_input.setPlaceholderText('输入密码返回桌面')
            self.pwd_input.setEnabled(True)  # 恢复密码输入
            if self.time_up:
                self.releaseMouse()
                QApplication.quit()

    def check_password(self):
        if self.normal_mode:
            if self.pwd_input.text() == self.password:
                self.releaseMouse()  # 释放鼠标捕获 不然会卡死!
                QApplication.quit()

    def closeEvent(self, event):
        self.releaseMouse()

if __name__ == '__main__':
    try:
        passwd = sys.argv[1]
    except IndexError as e:
        passwd = '11451419198110'
    app = QApplication(sys.argv)
    ex = StandbyApp(passwd)
    sys.exit(app.exec_())

