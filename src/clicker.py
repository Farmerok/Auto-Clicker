# imports
from sys import argv, exit
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QDoubleSpinBox, QComboBox, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSlot, QSize
from win32gui import FindWindow, EnumWindows, GetWindowText, IsWindow, PostMessage, IsWindowVisible
from win32con import WM_LBUTTONDOWN, WM_LBUTTONUP
from keyboard import add_hotkey, remove_hotkey, read_event
from time import sleep
from threading import Thread

class ClickerThread(QThread):
    def __init__(self, window_title, click_interval, parent=None):
        super().__init__(parent)
        self.window_title = window_title
        self.click_interval = click_interval
        self.running = False

    def find_window_by_title(self, title):
        hwnd = FindWindow(None, title)
   #     print(f"Window with title '{title}' found!" if hwnd else f"Window with title '{title}' not found!") # debug
        return hwnd

    def run(self):
        hwnd = self.find_window_by_title(self.window_title)
        if not hwnd: return

        while self.running:
            if not IsWindow(hwnd):
                hwnd = self.find_window_by_title(self.window_title)
                if not hwnd: 
                    self.running = False
                    continue

            PostMessage(hwnd, WM_LBUTTONDOWN, 0, 0)
            PostMessage(hwnd, WM_LBUTTONUP, 0, 0)
            sleep(self.click_interval)

    def start_clicking(self):
        self.running = True
        if not self.isRunning():
            self.start()

    def stop_clicking(self):
        self.running = False
        self.wait() 

class ClickerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.hotkey = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Auto Clicker')
        self.resize(400, 300)  # Initial size

        self.setStyleSheet("""
            QWidget { background-color: #2c2f33; color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 18px; }
            QPushButton { background-color: #7289da; border: none; padding: 15px; border-radius: 10px; color: white; font-weight: bold; font-size: 18px; }
            QPushButton:hover { background-color: #5b6eae; }
            QPushButton:pressed { background-color: #4a5d94; }
            QPushButton:disabled { background-color: #99aab5; }
            QLabel { font-size: 20px; font-weight: bold; padding-bottom: 10px; }
            QLineEdit, QDoubleSpinBox, QComboBox { padding: 10px; border-radius: 10px; border: 1px solid #5b6eae; font-size: 18px; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Window title and list
        window_layout = QVBoxLayout()
        self.title_label = QLabel('Window Title:')
        self.window_list = QComboBox()
        self.refresh_windows()
        window_layout.addWidget(self.title_label)
        window_layout.addWidget(self.window_list)
        layout.addLayout(window_layout)

        # Click interval
        interval_layout = QVBoxLayout()
        self.interval_label = QLabel('Click Interval (seconds):')
        self.interval_input = QDoubleSpinBox()
        self.interval_input.setRange(0.1, float('inf'))
        self.interval_input.setSingleStep(0.1)
        interval_layout.addWidget(self.interval_label)
        interval_layout.addWidget(self.interval_input)
        layout.addLayout(interval_layout)

        # Hotkey
        hotkey_layout = QVBoxLayout()
        self.hotkey_label = QLabel('Hotkey:')
        self.hotkey_input = QLineEdit()
        self.assign_hotkey_button = QPushButton('Assign Hotkey')
        self.assign_hotkey_button.clicked.connect(self.assign_hotkey)
        hotkey_layout.addWidget(self.hotkey_label)
        hotkey_layout.addWidget(self.hotkey_input)
        hotkey_layout.addWidget(self.assign_hotkey_button)
        layout.addLayout(hotkey_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton('Refresh Window List')
        self.start_button = QPushButton('Start')
        self.stop_button = QPushButton('Stop')

        self.refresh_button.clicked.connect(self.refresh_windows)
        self.start_button.clicked.connect(self.start_clicking)
        self.stop_button.clicked.connect(self.stop_clicking)

        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

    def refresh_windows(self):
        self.window_list.clear()
        window_titles = []
        EnumWindows(lambda hwnd, results: results.append(GetWindowText(hwnd)) if GetWindowText(hwnd) and IsWindowVisible(hwnd) else None, window_titles)
        self.window_list.addItems(window_titles)

    @pyqtSlot()
    def start_clicking(self):
        window_title = self.window_list.currentText()
        click_interval = self.interval_input.value()
        if click_interval <= 0:
            QMessageBox.warning(self, 'Warning', 'Click interval must be greater than 0.')
            return
        if hasattr(self, 'clicker_thread') and self.clicker_thread.isRunning():
            self.clicker_thread.stop_clicking()
        self.clicker_thread = ClickerThread(window_title, click_interval)
        self.clicker_thread.start_clicking()

    @pyqtSlot()
    def stop_clicking(self):
        if hasattr(self, 'clicker_thread'):
            self.clicker_thread.stop_clicking()

    def assign_hotkey(self):
        self.hotkey_input.setText('Press any key...')
        self.hotkey_input.setDisabled(True)
        Thread(target=self.wait_for_hotkey).start()

    def wait_for_hotkey(self):
        event = read_event(suppress=True)
        if event.event_type == 'down':
            new_hotkey = event.name
            self.change_hotkey(new_hotkey)
            self.hotkey_input.setText(new_hotkey)
            self.hotkey_input.setDisabled(False)

    def change_hotkey(self, new_hotkey):
        if self.hotkey:
            remove_hotkey(self.hotkey)
        self.hotkey = new_hotkey
        add_hotkey(new_hotkey, self.toggle_clicking)

    def toggle_clicking(self):
        if hasattr(self, 'clicker_thread') and self.clicker_thread.running:
            self.stop_clicking()
        else:
            self.start_clicking()

if __name__ == '__main__':
    app = QApplication(argv)
    ex = ClickerApp()
    ex.show()
    exit(app.exec_())
