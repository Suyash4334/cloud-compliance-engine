import sys
import time
import requests

try:
    from platform_utils import get_active_window_title, play_alert_sound, is_azure_active
except ImportError:
    # Direct fallback if platform_utils is in same directory
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from platform_utils import get_active_window_title, play_alert_sound, is_azure_active

def run_azure_compliance_audit():
    """Simulated or live Azure compliance status check."""
    return {"compliance_score": 92.5, "total_checked": 3, "failures": 0}

# Try importing PyQt6; if not installed, provide Headless Watchdog fallback
try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtGui import QPainter, QPen, QColor
    HAS_PYQT6 = True
except ImportError:
    HAS_PYQT6 = False


if HAS_PYQT6:
    class AzureWatchdogWorker(QThread):
        azure_status_signal = pyqtSignal(bool, int, str)

        def run(self):
            last_sent_title = ""
            while True:
                current_title = ""
                azure_open = False
                try:
                    current_title = get_active_window_title()
                    if current_title and is_azure_active(current_title):
                        azure_open = True
                except Exception as e:
                    print(f"[WATCHDOG ERROR] {e}")

                failures = 0
                if azure_open:
                    # Sync to local FastAPI backend when title changes
                    if current_title and current_title != last_sent_title:
                        try:
                            requests.post(
                                "http://127.0.0.1:8000/api/log-activity",
                                json={"action": current_title},
                                timeout=1
                            )
                            last_sent_title = current_title
                            print(f"[SYNC] Logged activity to dashboard: {current_title}")
                        except Exception:
                            pass

                    audit_data = run_azure_compliance_audit()
                    if audit_data and audit_data.get("failures", 0) > 0:
                        failures = audit_data.get("failures", 0)
                        play_alert_sound(1200, 400)

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
                    print(f"[HUD] Azure Detected ({title}). HUD ON.")
                else:
                    self.hide()
                    print("[HUD] Switched away from Azure. HUD OFF.")

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


def run_headless_watchdog():
    """Runs cross-platform watchdog in CLI mode when GUI library (PyQt6) is not installed."""
    print("=" * 60)
    print(" [WATCHDOG] Running in Cross-Platform Headless CLI Mode")
    print(f" [PLATFORM] Operating System: {sys.platform}")
    print(" [INFO] Install PyQt6 ('pip install PyQt6') for Desktop HUD overlay.")
    print(" [INFO] Actively polling for Azure Portal window & streaming telemetry...")
    print("=" * 60)

    last_sent_title = ""
    is_active = False

    try:
        while True:
            current_title = get_active_window_title()
            azure_open = is_azure_active(current_title)

            if azure_open != is_active:
                is_active = azure_open
                if is_active:
                    print(f"\n🚨 [AZURE DETECTED] Focused Window: '{current_title}'")
                else:
                    print("\n💤 [AZURE INACTIVE] Switched focus away.")

            if is_active and current_title and current_title != last_sent_title:
                try:
                    requests.post(
                        "http://127.0.0.1:8000/api/log-activity",
                        json={"action": current_title},
                        timeout=1
                    )
                    last_sent_title = current_title
                    print(f" [SYNC] -> Synced to Dashboard: '{current_title}'")
                except Exception as err:
                    print(f" [SYNC WARN] Backend offline: {err}")

                audit_data = run_azure_compliance_audit()
                if audit_data and audit_data.get("failures", 0) > 0:
                    play_alert_sound(1200, 400)

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[WATCHDOG] Stopped by user.")


if __name__ == "__main__":
    if "--cli" in sys.argv or "--headless" in sys.argv or not HAS_PYQT6:
        run_headless_watchdog()
    else:
        print(f"[HUD] Starting PyQt6 Visual Overlay on {sys.platform}...")
        app = QApplication(sys.argv)
        hud = HUDOverlay()
        hud.hide()  # Start hidden by default
        sys.exit(app.exec())