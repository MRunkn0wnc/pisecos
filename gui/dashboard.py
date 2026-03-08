import sys
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PiSecOS")
        self.setGeometry(0,0,1000,650)

        self.setStyleSheet("""
        QMainWindow {
            background-color: #0d021a;
        }

        QLabel {
            color: #c084fc;
            font-size: 22px;
        }

        QLineEdit {
            background-color: #1b0633;
            border: 2px solid #8b5cf6;
            padding: 6px;
            color: white;
        }

        QPushButton {
            background-color: #8b5cf6;
            color: black;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #a855f7;
        }

        QTextEdit {
            background-color: black;
            color: #39ff14;
            font-family: monospace;
        }
        """)

        layout = QVBoxLayout()

        title = QLabel("PiSecOS AI SECURITY CONSOLE")
        title.setAlignment(Qt.AlignCenter)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(30)
        glow.setColor(QColor("#a855f7"))
        glow.setOffset(0)
        title.setGraphicsEffect(glow)

        self.target = QLineEdit()
        self.target.setPlaceholderText("Enter Target Domain")

        self.scan_button = QPushButton("START RECON")
        self.scan_button.clicked.connect(self.start_scan)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.target)
        layout.addWidget(self.scan_button)
        layout.addSpacing(10)
        layout.addWidget(self.terminal)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def start_scan(self):

        target = self.target.text()

        if not target:
            return

        self.terminal.append(f"[+] Starting recon for {target}\n")

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_output)

        cmd = f"python core/recon_engine.py {target}"

        self.process.start("cmd", ["/c", cmd])

    def handle_output(self):

        data = self.process.readAllStandardOutput().data().decode()
        self.terminal.append(data)


app = QApplication(sys.argv)
window = Dashboard()
window.showFullScreen()
sys.exit(app.exec_())
