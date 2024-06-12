from sys import exit, argv
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpinBox, QPushButton, QRadioButton, QButtonGroup, QComboBox
from PyQt5.QtCore import Qt
from pyautogui import click, FailSafeException
from threading import Thread
from time import sleep
from keyboard import on_press_key

VERSION = "2.0"
class AutoClicker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clicking - OP Auto Clicker {}".format(VERSION))
        
        self.clicking = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Click interval
        interval_layout = QHBoxLayout()
        main_layout.addLayout(interval_layout)

        self.hours = QSpinBox()
        interval_layout.addWidget(QLabel("hours"), alignment=Qt.AlignRight)
        self.hours.setRange(0, 23)
        interval_layout.addWidget(self.hours)
        

        self.minutes = QSpinBox()
        interval_layout.addWidget(QLabel("mins"), alignment=Qt.AlignRight)
        self.minutes.setRange(0, 59)
        interval_layout.addWidget(self.minutes)

        self.seconds = QSpinBox()
        interval_layout.addWidget(QLabel("secs"), alignment=Qt.AlignRight)
        self.seconds.setRange(0, 59)
        interval_layout.addWidget(self.seconds)

        self.milliseconds = QSpinBox()
        interval_layout.addWidget(QLabel("milliseconds"), alignment=Qt.AlignRight)
        self.milliseconds.setRange(0, 999)
        interval_layout.addWidget(self.milliseconds)

        # Click options
        options_layout = QHBoxLayout()
        main_layout.addLayout(options_layout)
        options_layout.addWidget(QLabel("Mouse button"))
        self.mouse_button = QComboBox()
        self.mouse_button.addItems(["left", "right"])
        options_layout.addWidget(self.mouse_button)
        options_layout.addWidget(QLabel("Click type"))
        self.click_type = QComboBox()
        self.click_type.addItems(["single", "double"])
        options_layout.addWidget(self.click_type)

        # Click repeat
        repeat_layout = QVBoxLayout()
        main_layout.addLayout(repeat_layout)
        repeat_layout.addWidget(QLabel("Click repeat"))
        self.repeat_option_group = QButtonGroup(self)
        
        self.repeat = QRadioButton("Repeat")
        self.repeat_option_group.addButton(self.repeat)
        repeat_layout.addWidget(self.repeat)
        self.repeat_times = QSpinBox()
        self.repeat_times.setRange(1, 999999)
        repeat_layout.addWidget(self.repeat_times)
        self.repeat_until_stopped = QRadioButton("Repeat until stopped")
        self.repeat_option_group.addButton(self.repeat_until_stopped)
        repeat_layout.addWidget(self.repeat_until_stopped)

        # Cursor position
        cursor_layout = QHBoxLayout()
        main_layout.addLayout(cursor_layout)
        self.current_location = QRadioButton("Current location")
        self.current_location.setChecked(True)
        cursor_layout.addWidget(self.current_location)
        self.pick_location = QRadioButton("Pick location")
        cursor_layout.addWidget(self.pick_location)
        self.pick_x = QSpinBox()
        self.pick_x.setRange(0, 9999)
        cursor_layout.addWidget(self.pick_x)
        self.pick_y = QSpinBox()
        self.pick_y.setRange(0, 9999)
        cursor_layout.addWidget(self.pick_y)

        # Control buttons
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)
        self.start_button = QPushButton("Start (F7)")
        self.start_button.clicked.connect(self.start_clicking)
        control_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop (F7)")
        self.stop_button.clicked.connect(self.stop_clicking)
        control_layout.addWidget(self.stop_button)

        # Start listening for F7 keypress
        on_press_key("F7", self.toggle_clicking)

        # Apply styles
        self.setStyleSheet("""
            QWidget { background-color: #2c2f33; color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; }
            QPushButton { background-color: #7289da; border: none; padding: 10px; border-radius: 8px; color: white; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #5b6eae; }
            QPushButton:pressed { background-color: #4a5d94; }
            QPushButton:disabled { background-color: #99aab5; }
            QLabel { font-size: 14px; font-weight: bold; padding-bottom: 8px; }
            QSpinBox, QComboBox { padding: 8px; border-radius: 8px; border: 1px solid #5b6eae; font-size: 14px; }
        """)

    def toggle_clicking(self, event=None):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.click_thread = Thread(target=self.click_loop)
            self.click_thread.start()
            print("Clicking started")

    def stop_clicking(self):
        self.clicking = False
        print("Clicking stopped")

    def click_loop(self):
        hours = self.hours.value()
        minutes = self.minutes.value()
        seconds = self.seconds.value()
        milliseconds = self.milliseconds.value()
        interval = (hours * 3600 + minutes * 60 + seconds) + milliseconds / 1000

        repeat_times = self.repeat_times.value() if not self.repeat_until_stopped.isChecked() else float('inf')
        try:
            while self.clicking and repeat_times > 0:
                if not self.current_location.isChecked():
                    x = self.pick_x.value()
                    y = self.pick_y.value()
                    click(x=x, y=y, button=self.mouse_button.currentText(), clicks=1 if self.click_type.currentText() == "single" else 2)
                else:
                    click(button=self.mouse_button.currentText(), clicks=1 if self.click_type.currentText() == "single" else 2)

                repeat_times -= 1
                sleep(interval)

            self.clicking = False
            print("Click loop finished")
        except FailSafeException:
            self.clicking = False
            print("Error. Clicker stoped ")    

if __name__ == "__main__":
    app = QApplication(argv)
    auto_clicker = AutoClicker()
    auto_clicker.show()
    exit(app.exec_())