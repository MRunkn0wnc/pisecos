#!/usr/bin/env python3
"""
PiSecOS Professional GUI - AEGIS AI Pentesting Platform
Complete with attack selector, live terminal, AI chat, and report preview
"""

import sys
import os
import json
import threading
import queue
import time
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Import core modules
from core.workflow_orchestrator import WorkflowOrchestrator
from core.ai_engine import AEGIS
from core.tool_engine import ToolEngine
from core.recon_engine import run_recon
from core.report_engine import generate_report

# ============================================================================
# THEME
# ============================================================================

class CyberTheme:
    """Professional dark theme for pentesting"""
    BG_DARK = "#0a0a0a"
    BG_PANEL = "#1a1a1a"
    BG_DARKER = "#0f0f0f"
    BG_INPUT = "#2a2a2a"
    
    TEXT_PRIMARY = "#00ff41"  # Matrix green
    TEXT_SECONDARY = "#00ccff"  # Cyan
    TEXT_ACCENT = "#aa00ff"  # Purple
    TEXT_ERROR = "#ff4444"  # Red
    TEXT_WARNING = "#ffaa00"  # Orange
    TEXT_SUCCESS = "#00ff41"  # Green
    TEXT_NORMAL = "#e0e0e0"  # Light gray
    TEXT_DIM = "#808080"  # Gray
    
    BORDER = "#00ff41"
    BORDER_FOCUS = "#00ccff"
    
    BUTTON_BG = "#2a2a2a"
    BUTTON_HOVER = "#00ff41"
    BUTTON_TEXT = "#ffffff"


class QFlowLayout(QLayout):
    """Custom flow layout for suggestion chips"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_list = []
        
    def __del__(self):
        while self.item_list:
            item = self.item_list.pop()
            item.deleteLater()
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        return self.do_layout(QRect(0, 0, width, 0), True)
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size
    
    def do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            style = item.widget().style() if item.widget() else None
            space = spacing + (style.pixelMetric(style.PM_LayoutHorizontalSpacing) if style else 0)
            next_x = x + item.sizeHint().width() + space
            
            if next_x - space > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space
                next_x = x + item.sizeHint().width() + space
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()


# ============================================================================
# ATTACK SELECTOR WIDGET
# ============================================================================

class AttackSelector(QWidget):
    """Widget for selecting attack types and profiles"""
    
    attackSelected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.attack_profiles = self.load_profiles()
        self.init_ui()
        
    def load_profiles(self):
        """Load attack profiles from config"""
        return {
            "Quick Scan": {
                "phases": ["recon", "port_scan"],
                "description": "Basic reconnaissance and port scanning",
                "time": "2-5 minutes"
            },
            "Full Recon": {
                "phases": ["recon", "port_scan", "service_detection", "vuln_scan"],
                "description": "Complete information gathering",
                "time": "10-20 minutes"
            },
            "Web App Test": {
                "phases": ["recon", "web_enum", "sqli", "vuln_scan"],
                "description": "Comprehensive web application testing",
                "time": "15-30 minutes"
            },
            "Network Pentest": {
                "phases": ["port_scan", "service_detection", "vuln_scan", "exploit"],
                "description": "Internal network penetration test",
                "time": "20-40 minutes"
            },
            "Wireless Audit": {
                "phases": ["wifi_discovery", "handshake_capture", "password_crack"],
                "description": "Wireless network security assessment",
                "time": "30-60 minutes"
            },
            "Exploit Focus": {
                "phases": ["vuln_scan", "exploit"],
                "description": "Aggressive exploitation testing",
                "time": "15-25 minutes"
            }
        }
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("[TARGET] ATTACK SELECTOR")
        title.setStyleSheet(f"""
            color: {CyberTheme.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
            border-bottom: 1px solid {CyberTheme.TEXT_PRIMARY};
        """)
        layout.addWidget(title)
        
        # Attack type checkboxes
        self.attack_types = {}
        attacks = [
            ("Reconnaissance", "recon", CyberTheme.TEXT_SECONDARY),
            ("Web Testing", "web", CyberTheme.TEXT_ACCENT),
            ("Network Scan", "network", CyberTheme.TEXT_PRIMARY),
            ("Wireless", "wireless", CyberTheme.TEXT_WARNING),
            ("Exploitation", "exploit", CyberTheme.TEXT_ERROR),
            ("Password Cracking", "crack", CyberTheme.TEXT_WARNING)
        ]
        
        for label, key, color in attacks:
            cb = QCheckBox(label)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {CyberTheme.TEXT_NORMAL};
                    font-size: 12px;
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {color};
                    border-radius: 3px;
                    background: {CyberTheme.BG_DARKER};
                }}
                QCheckBox::indicator:checked {{
                    background: {color};
                }}
            """)
            self.attack_types[key] = cb
            layout.addWidget(cb)
        
        layout.addSpacing(10)
        
        # Attack profile dropdown
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Profile:"))
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.attack_profiles.keys())
        self.profile_combo.setStyleSheet(f"""
            QComboBox {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid {CyberTheme.TEXT_PRIMARY};
                border-top: 5px solid transparent;
                border-bottom: 5px solid transparent;
            }}
        """)
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        profile_layout.addWidget(self.profile_combo)
        layout.addLayout(profile_layout)
        
        # Profile description
        self.profile_desc = QLabel("")
        self.profile_desc.setWordWrap(True)
        self.profile_desc.setStyleSheet(f"""
            color: {CyberTheme.TEXT_DIM};
            font-size: 11px;
            padding: 5px;
            background: {CyberTheme.BG_DARKER};
            border-radius: 3px;
        """)
        layout.addWidget(self.profile_desc)
        
        # Profile time estimate
        self.profile_time = QLabel("")
        self.profile_time.setStyleSheet(f"""
            color: {CyberTheme.TEXT_SECONDARY};
            font-size: 11px;
        """)
        layout.addWidget(self.profile_time)
        
        layout.addStretch()
        
        # Target input
        layout.addWidget(QLabel("Target:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("example.com or 192.168.1.1")
        self.target_input.setStyleSheet(f"""
            QLineEdit {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 3px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {CyberTheme.TEXT_SECONDARY};
            }}
        """)
        layout.addWidget(self.target_input)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("[START] ATTACK")
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.TEXT_SUCCESS};
                color: black;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {CyberTheme.TEXT_SECONDARY};
            }}
            QPushButton:disabled {{
                background: {CyberTheme.TEXT_DIM};
                color: {CyberTheme.BG_DARK};
            }}
        """)
        self.start_btn.clicked.connect(self.on_start_clicked)
        
        self.stop_btn = QPushButton("[STOP] ATTACK")
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.TEXT_ERROR};
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: #ff6666;
            }}
            QPushButton:disabled {{
                background: {CyberTheme.TEXT_DIM};
                color: {CyberTheme.BG_DARK};
            }}
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Show initial profile
        self.on_profile_changed(self.profile_combo.currentText())
    
    def on_profile_changed(self, profile_name):
        """Update description when profile changes"""
        profile = self.attack_profiles.get(profile_name, {})
        self.profile_desc.setText(f"Description: {profile.get('description', '')}")
        self.profile_time.setText(f"Est. time: {profile.get('time', 'Unknown')}")
        
        # Auto-check relevant attack types based on profile
        phases = profile.get('phases', [])
        for key, cb in self.attack_types.items():
            if key in str(phases):
                cb.setChecked(True)
    
    def on_start_clicked(self):
        """Start attack button clicked"""
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "No Target", "Please enter a target")
            return
        
        # Gather selected attacks
        selected = [key for key, cb in self.attack_types.items() if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "No Attacks", "Please select at least one attack type")
            return
        
        # Get profile
        profile = self.profile_combo.currentText()
        
        attack_config = {
            'target': target,
            'attacks': selected,
            'profile': profile,
            'phases': self.attack_profiles.get(profile, {}).get('phases', [])
        }
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.attackSelected.emit(attack_config)
    
    def on_stop_clicked(self):
        """Stop attack button clicked"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.attackSelected.emit({'stop': True})
    
    def reset(self):
        """Reset after attack complete"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


# ============================================================================
# LIVE TERMINAL WIDGET
# ============================================================================

class LiveTerminal(QWidget):
    """Real-time terminal output with color coding"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_queue = queue.Queue()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_output)
        self.timer.start(100)  # Update every 100ms
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title with controls
        title_layout = QHBoxLayout()
        
        title = QLabel("[TERMINAL] LIVE OUTPUT")
        title.setStyleSheet(f"""
            color: {CyberTheme.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
        """)
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_DIM};
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
            }}
        """)
        self.clear_btn.clicked.connect(self.clear_output)
        title_layout.addWidget(self.clear_btn)
        
        layout.addLayout(title_layout)
        
        # Terminal output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Courier New", 10))
        self.output_area.setStyleSheet(f"""
            QTextEdit {{
                background: black;
                color: {CyberTheme.TEXT_PRIMARY};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 11px;
            }}
        """)
        layout.addWidget(self.output_area)
        
        self.setLayout(layout)
    
    def append(self, text, color=None):
        """Append text to terminal with optional color"""
        if color:
            html_color = {
                'green': CyberTheme.TEXT_PRIMARY,
                'cyan': CyberTheme.TEXT_SECONDARY,
                'purple': CyberTheme.TEXT_ACCENT,
                'red': CyberTheme.TEXT_ERROR,
                'yellow': CyberTheme.TEXT_WARNING,
                'white': CyberTheme.TEXT_NORMAL
            }.get(color, CyberTheme.TEXT_NORMAL)
            
            formatted = f'<span style="color: {html_color};">{text}</span>'
        else:
            formatted = text
        
        self.output_queue.put(formatted)
    
    def append_command(self, cmd):
        """Append a command with special formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(f"\n[{timestamp}] $ {cmd}", 'cyan')
    
    def append_result(self, result):
        """Append command result"""
        self.append(result, 'white')
    
    def append_error(self, error):
        """Append error message"""
        self.append(f"\n[!] ERROR: {error}", 'red')
    
    def append_success(self, msg):
        """Append success message"""
        self.append(f"\n[+] {msg}", 'green')
    
    def append_warning(self, msg):
        """Append warning message"""
        self.append(f"\n[!] {msg}", 'yellow')
    
    def update_output(self):
        """Update output from queue (called by timer)"""
        try:
            while True:
                text = self.output_queue.get_nowait()
                self.output_area.insertPlainText(text)
                # Auto-scroll to bottom
                cursor = self.output_area.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.output_area.setTextCursor(cursor)
        except queue.Empty:
            pass
    
    def clear_output(self):
        """Clear terminal output"""
        self.output_area.clear()


# ============================================================================
# AI CHAT PANEL
# ============================================================================

class AEGISChatPanel(QWidget):
    """AI chat interface for AEGIS"""
    
    chatMessage = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("[AI] AEGIS ASSISTANT")
        title.setStyleSheet(f"""
            color: {CyberTheme.TEXT_SECONDARY};
            font-size: 14px;
            font-weight: bold;
            border-bottom: 1px solid {CyberTheme.TEXT_SECONDARY};
            padding-bottom: 5px;
        """)
        layout.addWidget(title)
        
        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet(f"""
            QTextEdit {{
                background: {CyberTheme.BG_DARKER};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_SECONDARY};
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 11px;
            }}
        """)
        layout.addWidget(self.chat_history)
        
        # Quick suggestion chips
        suggestions_layout = QFlowLayout()
        
        suggestions = [
            "What should I scan first?",
            "Explain this finding",
            "Suggest next attack",
            "Generate report",
            "Check for exploits",
            "What's critical?"
        ]
        
        for suggestion in suggestions:
            chip = QPushButton(suggestion)
            chip.setStyleSheet(f"""
                QPushButton {{
                    background: {CyberTheme.BG_INPUT};
                    color: {CyberTheme.TEXT_SECONDARY};
                    border: 1px solid {CyberTheme.TEXT_SECONDARY};
                    border-radius: 15px;
                    padding: 5px 10px;
                    font-size: 10px;
                    max-height: 20px;
                }}
                QPushButton:hover {{
                    background: {CyberTheme.TEXT_SECONDARY};
                    color: black;
                }}
            """)
            chip.clicked.connect(lambda checked, s=suggestion: self.use_suggestion(s))
            suggestions_layout.addWidget(chip)
        
        layout.addLayout(suggestions_layout)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask AEGIS anything...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_SECONDARY};
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
            }}
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.TEXT_SECONDARY};
                color: black;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {CyberTheme.TEXT_PRIMARY};
            }}
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # Welcome message
        self.add_ai_message("I am AEGIS, your AI pentesting assistant. I'll help you find vulnerabilities and suggest attack vectors. What's our target?")
    
    def add_user_message(self, message):
        """Add user message to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_history.append(f'<span style="color: {CyberTheme.TEXT_PRIMARY};">[{timestamp}] You:</span> {message}')
    
    def add_ai_message(self, message):
        """Add AI message to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_history.append(f'<span style="color: {CyberTheme.TEXT_SECONDARY};">[{timestamp}] AEGIS:</span> {message}')
        self.chatMessage.emit(message)
    
    def send_message(self):
        """Send message to AEGIS"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        self.add_user_message(message)
        self.input_field.clear()
        
        # Send to orchestrator
        if hasattr(self.parent(), 'orchestrator'):
            self.parent().orchestrator.process_ai_query(message)
    
    def use_suggestion(self, suggestion):
        """Use suggestion chip"""
        self.input_field.setText(suggestion)
        self.send_message()


# ============================================================================
# REPORT PREVIEW WIDGET
# ============================================================================

class ReportPreview(QWidget):
    """Preview of scan results and findings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.findings = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("[REPORT] FINDINGS PREVIEW")
        title.setStyleSheet(f"""
            color: {CyberTheme.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
            border-bottom: 1px solid {CyberTheme.TEXT_PRIMARY};
            padding-bottom: 5px;
        """)
        layout.addWidget(title)
        
        # Summary stats
        stats_layout = QHBoxLayout()
        
        self.critical_count = QLabel("Critical: 0")
        self.critical_count.setStyleSheet(f"color: {CyberTheme.TEXT_ERROR}; font-weight: bold;")
        
        self.high_count = QLabel("High: 0")
        self.high_count.setStyleSheet(f"color: {CyberTheme.TEXT_WARNING}; font-weight: bold;")
        
        self.medium_count = QLabel("Medium: 0")
        self.medium_count.setStyleSheet(f"color: {CyberTheme.TEXT_SECONDARY}; font-weight: bold;")
        
        stats_layout.addWidget(self.critical_count)
        stats_layout.addWidget(self.high_count)
        stats_layout.addWidget(self.medium_count)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Findings tree
        self.findings_tree = QTreeWidget()
        self.findings_tree.setHeaderLabels(["Severity", "Finding", "Location", "Status"])
        self.findings_tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {CyberTheme.BG_DARKER};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 5px;
                padding: 5px;
                font-size: 11px;
            }}
            QTreeWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {CyberTheme.BG_PANEL};
            }}
            QTreeWidget::item:selected {{
                background: {CyberTheme.TEXT_PRIMARY};
                color: black;
            }}
        """)
        self.findings_tree.setColumnWidth(0, 80)
        self.findings_tree.setColumnWidth(1, 200)
        self.findings_tree.setColumnWidth(2, 100)
        layout.addWidget(self.findings_tree)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("[FILE] Export Full Report")
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {CyberTheme.TEXT_PRIMARY};
                color: black;
            }}
        """)
        self.export_btn.clicked.connect(self.export_report)
        
        self.copy_btn = QPushButton("[COPY] Copy Summary")
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {CyberTheme.TEXT_PRIMARY};
                color: black;
            }}
        """)
        self.copy_btn.clicked.connect(self.copy_summary)
        
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def add_finding(self, severity, finding, location, status="Open"):
        """Add a finding to the report"""
        item = QTreeWidgetItem(self.findings_tree)
        
        # Set color based on severity
        if severity == "CRITICAL":
            item.setForeground(0, QBrush(QColor(CyberTheme.TEXT_ERROR)))
        elif severity == "HIGH":
            item.setForeground(0, QBrush(QColor(CyberTheme.TEXT_WARNING)))
        elif severity == "MEDIUM":
            item.setForeground(0, QBrush(QColor(CyberTheme.TEXT_SECONDARY)))
        else:
            item.setForeground(0, QBrush(QColor(CyberTheme.TEXT_NORMAL)))
        
        item.setText(0, severity)
        item.setText(1, finding)
        item.setText(2, location)
        item.setText(3, status)
        
        self.findings.append({
            'severity': severity,
            'finding': finding,
            'location': location,
            'status': status
        })
        
        self.update_counts()
    
    def update_counts(self):
        """Update severity counts"""
        critical = sum(1 for f in self.findings if f['severity'] == 'CRITICAL')
        high = sum(1 for f in self.findings if f['severity'] == 'HIGH')
        medium = sum(1 for f in self.findings if f['severity'] == 'MEDIUM')
        
        self.critical_count.setText(f"Critical: {critical}")
        self.high_count.setText(f"High: {high}")
        self.medium_count.setText(f"Medium: {medium}")
    
    def clear_findings(self):
        """Clear all findings"""
        self.findings_tree.clear()
        self.findings = []
        self.update_counts()
    
    def export_report(self):
        """Export full report to file"""
        if not self.findings:
            QMessageBox.information(self, "No Findings", "No findings to export")
            return
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pisecos_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("="*60 + "\n")
                f.write("PISECOS SECURITY ASSESSMENT REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for finding in self.findings:
                    f.write(f"[{finding['severity']}] {finding['finding']}\n")
                    f.write(f"Location: {finding['location']}\n")
                    f.write(f"Status: {finding['status']}\n")
                    f.write("-"*40 + "\n")
            
            QMessageBox.information(self, "Report Saved", f"Report saved to {filename}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save report: {e}")
    
    def copy_summary(self):
        """Copy summary to clipboard"""
        if not self.findings:
            return
        
        summary = f"PiSecOS Findings Summary ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
        summary += "="*40 + "\n"
        
        critical = [f for f in self.findings if f['severity'] == 'CRITICAL']
        high = [f for f in self.findings if f['severity'] == 'HIGH']
        
        if critical:
            summary += "\nCRITICAL FINDINGS:\n"
            for f in critical:
                summary += f"  - {f['finding']} at {f['location']}\n"
        
        if high:
            summary += "\nHIGH FINDINGS:\n"
            for f in high:
                summary += f"  - {f['finding']} at {f['location']}\n"
        
        QApplication.clipboard().setText(summary)


# ============================================================================
# AI CONTROLS WIDGET
# ============================================================================

class AIControls(QWidget):
    """Controls for AI behavior"""
    
    modeChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("[CONFIG] AI CONTROLS")
        title.setStyleSheet(f"""
            color: {CyberTheme.TEXT_ACCENT};
            font-size: 14px;
            font-weight: bold;
            border-bottom: 1px solid {CyberTheme.TEXT_ACCENT};
            padding-bottom: 5px;
        """)
        layout.addWidget(title)
        
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Auto-pilot", "Semi-auto", "Manual", "Stealth"])
        self.mode_combo.setStyleSheet(f"""
            QComboBox {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_ACCENT};
                border-radius: 3px;
                padding: 5px;
            }}
        """)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)
        
        # Mode description
        self.mode_desc = QLabel("AI automatically chooses and runs attacks")
        self.mode_desc.setWordWrap(True)
        self.mode_desc.setStyleSheet(f"color: {CyberTheme.TEXT_DIM}; font-size: 10px;")
        layout.addWidget(self.mode_desc)
        
        layout.addSpacing(10)
        
        # Control buttons
        self.suggest_btn = QPushButton("[SUGGEST] Next Attack")
        self.suggest_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_SECONDARY};
                border: 1px solid {CyberTheme.TEXT_SECONDARY};
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {CyberTheme.TEXT_SECONDARY};
                color: black;
            }}
        """)
        self.suggest_btn.clicked.connect(self.suggest_attack)
        layout.addWidget(self.suggest_btn)
        
        self.explain_btn = QPushButton("[EXPLAIN] Current Findings")
        self.explain_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_PRIMARY};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {CyberTheme.TEXT_PRIMARY};
                color: black;
            }}
        """)
        self.explain_btn.clicked.connect(self.explain_findings)
        layout.addWidget(self.explain_btn)
        
        self.prioritize_btn = QPushButton("[PRIORITIZE] Vulnerabilities")
        self.prioritize_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_WARNING};
                border: 1px solid {CyberTheme.TEXT_WARNING};
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {CyberTheme.TEXT_WARNING};
                color: black;
            }}
        """)
        self.prioritize_btn.clicked.connect(self.prioritize_findings)
        layout.addWidget(self.prioritize_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Set initial description
        self.on_mode_changed("Auto-pilot")
    
    def on_mode_changed(self, mode):
        """Update description when mode changes"""
        descriptions = {
            "Auto-pilot": "AI automatically chooses and runs attacks based on findings",
            "Semi-auto": "AI suggests attacks, you approve before running",
            "Manual": "AI only explains findings, you run attacks manually",
            "Stealth": "AI avoids aggressive scans, focuses on passive recon"
        }
        self.mode_desc.setText(descriptions.get(mode, ""))
        self.modeChanged.emit(mode)
    
    def suggest_attack(self):
        """Suggest next attack based on current findings"""
        if hasattr(self.parent(), 'chat_panel'):
            self.parent().chat_panel.input_field.setText("What attack should I run next?")
            self.parent().chat_panel.send_message()
    
    def explain_findings(self):
        """Explain current findings"""
        if hasattr(self.parent(), 'chat_panel'):
            self.parent().chat_panel.input_field.setText("Explain the current findings")
            self.parent().chat_panel.send_message()
    
    def prioritize_findings(self):
        """Prioritize vulnerabilities"""
        if hasattr(self.parent(), 'chat_panel'):
            self.parent().chat_panel.input_field.setText("Prioritize the vulnerabilities found")
            self.parent().chat_panel.send_message()


# ============================================================================
# TOOL BROWSER WIDGET
# ============================================================================

class ToolBrowser(QWidget):
    """Tool browser for selecting and running tools"""
    
    toolSelected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tools_data = self.load_tools()
        self.init_ui()
        
    def load_tools(self):
        """Load tools from config"""
        try:
            config_path = "/usr/local/pisecos/configs/tool_sources.json"
            if os.path.exists(config_path):
                with open(config_path) as f:
                    return json.load(f)
        except:
            pass
        return {"known_tools": {}, "categories": {}}
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("[TOOLS] BROWSER")
        title.setStyleSheet(f"""
            color: {CyberTheme.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
            border-bottom: 1px solid {CyberTheme.TEXT_PRIMARY};
            padding-bottom: 5px;
        """)
        layout.addWidget(title)
        
        # Category selector
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Recon", "Scanner", "Web", "Cracker", "Exploit", "Wireless"])
        self.category_combo.currentTextChanged.connect(self.filter_tools)
        self.category_combo.setStyleSheet(f"""
            QComboBox {{
                background: {CyberTheme.BG_INPUT};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 3px;
                padding: 5px;
            }}
        """)
        layout.addWidget(self.category_combo)
        
        # Tool list
        self.tool_list = QListWidget()
        self.tool_list.setStyleSheet(f"""
            QListWidget {{
                background: {CyberTheme.BG_DARKER};
                color: {CyberTheme.TEXT_NORMAL};
                border: 1px solid {CyberTheme.TEXT_PRIMARY};
                border-radius: 5px;
                padding: 5px;
                font-size: 11px;
            }}
            QListWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {CyberTheme.BG_PANEL};
            }}
            QListWidget::item:selected {{
                background: {CyberTheme.TEXT_PRIMARY};
                color: black;
            }}
        """)
        self.tool_list.itemDoubleClicked.connect(self.on_tool_double_click)
        layout.addWidget(self.tool_list)
        
        # Tool info
        self.tool_info = QLabel("Double-click tool to run")
        self.tool_info.setWordWrap(True)
        self.tool_info.setStyleSheet(f"""
            color: {CyberTheme.TEXT_DIM};
            font-size: 10px;
            padding: 5px;
            background: {CyberTheme.BG_DARKER};
            border-radius: 3px;
        """)
        layout.addWidget(self.tool_info)
        
        self.setLayout(layout)
        self.load_all_tools()
    
    def load_all_tools(self):
        """Load all tools into list"""
        self.all_tools = list(self.tools_data.get('known_tools', {}).keys())
        self.tool_list.addItems(sorted(self.all_tools))
    
    def filter_tools(self, category):
        """Filter tools by category"""
        self.tool_list.clear()
        if category == "All":
            self.tool_list.addItems(sorted(self.all_tools))
        else:
            cat_key = category.lower()
            category_tools = self.tools_data.get('categories', {}).get(cat_key, [])
            self.tool_list.addItems(sorted(category_tools))
    
    def on_tool_double_click(self, item):
        """Handle tool double click"""
        tool_name = item.text()
        self.toolSelected.emit(tool_name)


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

class PiSecOSDashboard(QMainWindow):
    """Main PiSecOS Dashboard with all features"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PiSecOS - AEGIS AI Pentesting Platform")
        self.setGeometry(50, 50, 1600, 900)
        
        # Set window style
        self.setStyleSheet(f"background-color: {CyberTheme.BG_DARK};")
        
        # Initialize orchestrator with callbacks
        self.orchestrator = WorkflowOrchestrator(
            output_callback=self.on_orchestrator_output,
            finding_callback=self.on_orchestrator_finding,
            chat_callback=self.on_orchestrator_chat
        )
        
        # Attack state
        self.current_target = None
        self.attack_running = False
        
        # Initialize UI
        self.init_ui()
        
        # Show welcome message
        self.show_welcome()
    
    def init_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout - 4 quadrants
        main_layout = QGridLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Top row - 3 columns
        # Left: Attack Selector
        self.attack_selector = AttackSelector(self)
        self.attack_selector.attackSelected.connect(self.on_attack_selected)
        main_layout.addWidget(self.attack_selector, 0, 0)
        
        # Middle: Live Terminal (larger)
        self.terminal = LiveTerminal(self)
        main_layout.addWidget(self.terminal, 0, 1, 2, 1)  # Span 2 rows
        
        # Right: AI Chat
        self.chat_panel = AEGISChatPanel(self)
        self.chat_panel.chatMessage.connect(self.on_chat_message)
        main_layout.addWidget(self.chat_panel, 0, 2)
        
        # Bottom row - 2 columns
        # Bottom Left: Report Preview
        self.report_preview = ReportPreview(self)
        main_layout.addWidget(self.report_preview, 1, 0)
        
        # Bottom Right: AI Controls
        self.ai_controls = AIControls(self)
        self.ai_controls.modeChanged.connect(self.on_ai_mode_changed)
        main_layout.addWidget(self.ai_controls, 1, 2)
        
        # Set column/row stretches
        main_layout.setColumnStretch(0, 2)  # Attack selector
        main_layout.setColumnStretch(1, 4)  # Terminal (largest)
        main_layout.setColumnStretch(2, 2)  # Chat + Controls
        
        main_layout.setRowStretch(0, 3)  # Top row
        main_layout.setRowStretch(1, 2)  # Bottom row
        
        central.setLayout(main_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: {CyberTheme.BG_PANEL};
                color: {CyberTheme.TEXT_NORMAL};
                border-top: 1px solid {CyberTheme.TEXT_PRIMARY};
                font-size: 11px;
            }}
        """)
        
        # Status widgets
        self.target_status = QLabel("Target: Not set")
        self.mode_status = QLabel("Mode: Auto-pilot")
        self.ai_status = QLabel("AEGIS: Ready")
        
        self.status_bar.addWidget(self.target_status)
        self.status_bar.addPermanentWidget(self.mode_status)
        self.status_bar.addPermanentWidget(self.ai_status)
    
    def show_welcome(self):
        """Show welcome message in terminal"""
        self.terminal.append("="*60, 'cyan')
        self.terminal.append("PiSecOS - AEGIS AI Pentesting Platform", 'green')
        self.terminal.append("="*60, 'cyan')
        self.terminal.append("\nWelcome! I'm AEGIS, your AI pentesting assistant.", 'white')
        self.terminal.append("\nTo get started:", 'white')
        self.terminal.append("  1. Enter a target (IP or domain)", 'white')
        self.terminal.append("  2. Select attack types or choose a profile", 'white')
        self.terminal.append("  3. Click START ATTACK", 'white')
        self.terminal.append("\nI'll guide you through the process and explain everything.\n", 'green')
    
    def on_orchestrator_output(self, text, color=None):
        """Handle output from orchestrator"""
        self.terminal.append(text, color)
    
    def on_orchestrator_finding(self, severity, finding, location):
        """Handle finding from orchestrator"""
        self.report_preview.add_finding(severity, finding, location)
    
    def on_orchestrator_chat(self, message, is_user=False):
        """Handle chat message from orchestrator"""
        if is_user:
            self.chat_panel.add_user_message(message)
        else:
            self.chat_panel.add_ai_message(message)
    
    def on_attack_selected(self, config):
        """Handle attack start/stop"""
        if config.get('stop'):
            self.orchestrator.stop_attack()
            self.attack_selector.reset()
            return
        
        target = config['target']
        self.current_target = target
        self.target_status.setText(f"Target: {target}")
        
        # Start attack via orchestrator
        self.orchestrator.start_attack(target, config)
        
        # Update UI
        self.attack_selector.start_btn.setEnabled(False)
        self.attack_selector.stop_btn.setEnabled(True)
    
    def on_chat_message(self, message):
        """Handle messages from AI chat"""
        pass  # Already handled by orchestrator
    
    def on_ai_mode_changed(self, mode):
        """Handle AI mode change"""
        self.mode_status.setText(f"Mode: {mode}")
        self.orchestrator.set_ai_mode(mode.lower())
        self.terminal.append(f"\n[AI] Mode changed to: {mode}", 'purple')
    
    def closeEvent(self, event):
        """Handle window close"""
        self.orchestrator.shutdown()
        event.accept()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyle('Fusion')
    
    # Create and show dashboard
    dashboard = PiSecOSDashboard()
    dashboard.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()