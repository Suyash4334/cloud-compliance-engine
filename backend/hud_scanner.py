import sys
import time
import winsound
import win32gui
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor

try:
    from azure_scanner import run_azure_compliance_audit
except ImportError:
    def run_azure_compliance_audit():
        return {"compliance_score": 100.0, "total_checked": 0, "failures": 0}

class AzureWatchdogWorker(QThread):
    azure_status_signal = pyqtSignal(bool, int, str)

    def run(self):
        last_sent_title = ""
        while True:
            azure_open = False
            current_title = ""
            try:
                hwnd = win32gui.GetForegroundWindow()
                current_title = win32gui.GetWindowText(hwnd)
                
                # Debug print to check active window titles in real-time on your terminal
                if current_title:
                    print(f"[DEBUG] Active Window Title: {current_title}")

                if current_title and ("Microsoft Azure" in current_title or "Azure" in current_title or "portal.azure.com" in current_title):
                    azure_open = True
            except Exception as e:
                print(f"[ERROR] {e}")
                pass

            failures = 0
            if azure_open:
                # Send the exact active Azure blade/page title to FastAPI backend
                if current_title != last_sent_title:
                    try:
                        requests.post("http://127.0.0.1:8000/api/log-activity", json={"action": current_title})
                        last_sent_title = current_title
                        print(f"[SYNC] Logged activity to website: {current_title}")
                    except Exception as err:
                        print(f"[SYNC ERROR] {err}")

                audit_data = run_azure_compliance_audit()
                if audit_data and audit_data.get("failures", 0) > 0:
                    failures = audit_data.get("failures")
                    try:
                        winsound.Beep(1200, 400)
                    except:
                        pass

            self.azure_status_signal.emit(azure_open, failures, current_title)
            time.sleep(1)

class HUDOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.has_threat = False
        self.wave_offset = -50  
        self.scan_completed = False
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_wave)
        self.anim_timer.start(25)

        self.worker = AzureWatchdogWorker()
        self.worker.azure_status_signal.connect(self.handle_azure_status)
        self.worker.start()

    def handle_azure_status(self, azure_open, failures, title):
        if azure_open != self.is_active:
            self.is_active = azure_open
            if azure_open:
                self.wave_offset = -50
                self.scan_completed = False
                self.show()
                self.raise_()
                print("[HUD] Azure Portal Focused -> SHOWN")
            else:
                self.hide()
                print("[HUD] Switched away -> HIDDEN")

        self.has_threat = (failures > 0)
        self.update()

    def update_wave(self):
        if self.is_active and not self.scan_completed:
            self.wave_offset += 25
            if self.wave_offset > self.height():
                self.scan_completed = True
            self.update()

    def paintEvent(self, event):
        if not self.is_active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        border_color = QColor(239, 68, 68, 220) if self.has_threat else QColor(59, 130, 246, 180)
        pen = QPen(border_color, 3)
        painter.setPen(pen)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawRect(rect)

        if not self.scan_completed:
            wave_pen = QPen(QColor(96, 165, 250, 200), 2, Qt.PenStyle.DashLine)
            painter.setPen(wave_pen)
            painter.drawLine(0, self.wave_offset, self.width(), self.wave_offset)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = HUDOverlay()
    hud.hide() # Force hidden on startup
    sys.exit(app.exec())