import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.aegis import execute


class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PiSecOS")
        self.setGeometry(0, 0, 1200, 700)

        self.setStyleSheet("""
        QMainWindow {
            background-color:#0d021a;
        }

        QLabel {
            color:#c084fc;
            font-size:20px;
        }

        QTextEdit {
            background-color:black;
            color:#39ff14;
            font-family:monospace;
        }

        QLineEdit {
            background:#1b0633;
            color:white;
            border:2px solid #8b5cf6;
            padding:6px;
        }

        QPushButton {
            background:#8b5cf6;
            padding:8px;
            font-weight:bold;
        }

        QPushButton:hover {
            background:#a855f7;
        }
        """)

        main_layout = QVBoxLayout()

        title = QLabel("PiSecOS AI SECURITY CONSOLE")
        title.setAlignment(Qt.AlignCenter)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(25)
        glow.setColor(QColor("#a855f7"))
        title.setGraphicsEffect(glow)

        main_layout.addWidget(title)

        panels = QHBoxLayout()

        # AI assistant panel
        self.assistant = QTextEdit()
        self.assistant.setReadOnly(True)
        self.assistant.append("AEGIS AI Assistant Ready\n")
        self.assistant.append("Example commands:")
        self.assistant.append("scan example.com")
        self.assistant.append("subdomains example.com")
        self.assistant.append("ports example.com")

        panels.addWidget(self.assistant)

        # terminal panel
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)

        panels.addWidget(self.terminal)

        main_layout.addLayout(panels)

        # command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.returnPressed.connect(self.run_command)

        main_layout.addWidget(self.command_input)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

    def run_command(self):

        command = self.command_input.text()

        if not command:
            return

        self.terminal.append(f"> {command}")

        result = execute(command)

        self.terminal.append(result)

        self.command_input.clear()


app = QApplication(sys.argv)

window = Dashboard()
window.showFullScreen()

sys.exit(app.exec_())