#!/usr/bin/env python
"""
2025.2.6
黄学之
计算练习小助手
"""
import logging
import sys
from random import randint, choice

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
                             QDialog, QSpinBox, QCheckBox, QFormLayout, QHBoxLayout,
                             QMessageBox, QLineEdit, QLCDNumber)

# ----------------------------------- 日志配置 -----------------------------------
"""
使用官方日志库 以便于结束后回顾答题过程
"""
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('math_game.log'), # 答题日志存储在同目录下的'math_game.log'文件中
        logging.StreamHandler()
    ]
)
global logger
logger = logging.getLogger(__name__)

# ----------------------------------- 游戏核心 -----------------------------------
class QuestionGenerator:
    def __init__(self, allow_negative):
        self.allow_negative = allow_negative

    def generate(self, difficulty_level):
        max_number = difficulty_level * 10
        operator = choice(['plus', 'minus', 'divide', 'times'])
        method = getattr(self, f'_generate_{operator}')
        return method(max_number)

    def _generate_plus(self, max_num):
        if self.allow_negative:
            a = randint(-max_num, max_num)
            b = randint(-max_num, max_num)
        else:
            a = randint(0, max_num)
            b = randint(0, max_num)
        #logger.info(msg=str(a+b)) # DEBUG
        return f"{a} + {b} = ?", a + b

    def _generate_minus(self, max_num):
        if self.allow_negative:
            a = randint(-max_num, max_num)
            b = randint(-max_num, max_num)
        else:
            a = randint(0, max_num)
            b = randint(0, max_num)
            if a < b:
                a, b = b, a
        #logger.info(msg=str(a-b)) # DEBUG
        return f"{a} - {b} = ?", a - b

    def _generate_times(self, max_num):
        if self.allow_negative:
            a = randint(-max_num, max_num)
            b = randint(-max_num,max_num)
        else:
            a = randint(0, max_num)
            b = randint(0, max_num)
        #logger.info(msg=str(a*b)) # DEBUG
        return f"{a} × {b} = ?", a * b

    def _generate_divide(self, max_num):
        #enable_negative = False
        #if enable_negative:
        if self.allow_negative:
            a = randint(-max_num, max_num)
            b = a * randint(-max_num, max_num)
        else:
            a = randint(0, max_num)
            b = a * randint(0, max_num)
        logger.info(msg=str(a//b)) # DEBUG
        return f"{b} ÷ {a} = ?", b // a


# ----------------------------------- 游戏界面 -----------------------------------
class GameWindow(QWidget):
    def __init__(self, settings,difficulty):
        super().__init__()
        self.settings = settings
        self.score = 0
        self.difficulty = difficulty
        self.question_gen = QuestionGenerator(settings['allow_negative'])
        self.init_ui()
        self.start_game()

    def init_ui(self):
        self.setWindowTitle('计算练习小助手')
        self.setMinimumSize(600, 450)

        self.score_label = QLabel(f"得分: {self.score}")
        self.score_label.setAlignment(Qt.AlignCenter)

        self.timer_lcd = QLCDNumber()
        self.timer_lcd.setDigitCount(8)

        self.question_label = QLabel()
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont('Arial', 24))

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("输入你的答案")
        self.answer_input.returnPressed.connect(self.check_answer)

        self.submit_btn = QPushButton('点击提交(或点击Enter键)')
        self.submit_btn.clicked.connect(self.check_answer)
        self.giveup_btn = QPushButton('退出答题')
        self.giveup_btn.clicked.connect(self.close)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.score_label)
        layout.addWidget(self.timer_lcd)
        layout.addWidget(self.question_label)
        layout.addWidget(self.answer_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.giveup_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.init_timer()

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.time_left = self.settings['time_limit']
        self.timer_lcd.display(self.format_time(self.time_left))
        self.timer.start(1000)

    def format_time(self, seconds):
        return f"{seconds // 60:02}:{seconds % 60:02}"

    def update_timer(self):
        self.time_left -= 1
        self.timer_lcd.display(self.format_time(self.time_left))

        if self.time_left <= 0:
            self.timer.stop()
            QMessageBox.warning(self, "时间到!",f"你真棒!\n最终得分: {self.score}\n")
            logger.info(f"最终得分: {self.score}\n")
            self.close()

    def start_game(self):
        self.new_question()
        self.answer_input.setFocus()

    def new_question(self):
        question, answer = self.question_gen.generate(self.difficulty)
        self.current_question = question
        self.current_answer = answer
        self.question_label.setText(question)
        self.answer_input.clear()

        # 每得5分增加难度 提高计算游戏刺激性
        if self.score > 0 and self.score % 5 == 0:
            self.difficulty += 1

    def check_answer(self):
        try:
            user_answer = int(self.answer_input.text())
        except ValueError:
            QMessageBox.warning(self, "输入无效", "请输入一个数字!")
            logger.warning("输入无效, 请输入一个数字!")
            return
        logger.info(msg=f"答案:{str(user_answer)}")
        if user_answer == self.current_answer:
            self.score += 1
            logger.info(msg='答案正确')
            self.score_label.setText(f"当前得分: {self.score}")
            if self.settings['single_timer']:
                self.reset_timer()
            self.new_question()
        else:
            QMessageBox.critical(self, "答错了!", f"正确答案是 {self.current_answer},答题结束,得分{self.score}")
            logger.info(f"答案错误, 正确答案是 {self.current_answer},答题结束,得分{self.score}")
            self.close()

    def reset_timer(self):
        self.time_left = self.settings['time_limit']
        self.timer_lcd.display(self.format_time(self.time_left))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("答题设置")
        self.setMinimumSize(350, 250)
        self.init_ui()

    def init_ui(self):
        self.time_spin = QSpinBox()
        self.time_spin.setRange(30, 3600)
        self.time_spin.setValue(60)
        self.time_spin.setSuffix(" 秒")

        self.negative_check = QCheckBox("启用负数(包括答案)")
        self.timer_check = QCheckBox("在题目答对后增加时间")

        self.start_btn = QPushButton("开始答题!")
        self.cancel_btn = QPushButton("取消")

        form_layout = QFormLayout()
        form_layout.addRow("剩余时间:", self.time_spin)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.negative_check)
        main_layout.addWidget(self.timer_check)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # 信号连接 没了这个按钮作废
        self.start_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)


# ----------------------------------- 主程序 -----------------------------------
class MathGame:
    def __init__(self,difficulty):
        self.app = QApplication(sys.argv)
        self.main_window = QWidget()
        self.init_main_window()
        self.difficulty = int(difficulty)


    def init_main_window(self):
        self.main_window.setWindowTitle("计算练习小助手")
        self.main_window.setFixedSize(450, 300)

        layout = QVBoxLayout()
        title = QLabel("计算练习小助手")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 18))

        start_btn = QPushButton("开始练习")
        start_btn.clicked.connect(self.show_settings)

        quit_btn = QPushButton("退出程序")
        quit_btn.clicked.connect(self.app.quit)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(start_btn)
        layout.addWidget(quit_btn)
        layout.addStretch()

        self.main_window.setLayout(layout)
        self.main_window.show()

    def show_settings(self):
        dialog = SettingsDialog(self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            settings = {
                'time_limit': dialog.time_spin.value(),
                'allow_negative': dialog.negative_check.isChecked(),
                'single_timer': dialog.timer_check.isChecked()
            }
            self.start_game(settings)

    def start_game(self, settings):
        try:
            self.game_window = GameWindow(settings,self.difficulty)
            self.game_window.show()
        except Exception as e:
            QMessageBox.critical(self.main_window, "出现错误",
                                 f"无法启动练习程序:\n{str(e)}")
            logger.critical(msg=f"无法启动练习程序:\n{str(e)}")
    def run(self):
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    try:
        difficulty = sys.argv[1]
    except IndexError as e:
        difficulty = 1
    logger.info(msg=f"将难度设置为 {difficulty}.")
    game = MathGame(difficulty)
    sys.exit(game.app.exec_())