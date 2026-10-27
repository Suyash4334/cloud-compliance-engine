"""
Cross-Platform Utilities for Cloud Compliance Engine Watchdog.
Supports Windows, macOS (Darwin), and Linux seamlessly.
"""

import sys
import os
import subprocess

def get_active_window_title() -> str:
    """
    Returns the title of the currently focused/active window.
    Works across Windows, macOS, and Linux without hard crashes.
    """
    platform = sys.platform

    # --- Windows Implementation ---
    if platform == "win32":
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                title = win32gui.GetWindowText(hwnd)
                if title:
                    return title.strip()
        except ImportError:
            pass
        except Exception:
            pass

        try:
            import pygetwindow as gw
            title = gw.getActiveWindowTitle()
            if title:
                return title.strip()
        except ImportError:
            pass
        except Exception:
            pass
        return ""

    # --- macOS (Darwin) Implementation ---
    elif platform == "darwin":
        try:
            # 1. Query frontmost application process name
            app_script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            res_app = subprocess.run(
                ["osascript", "-e", app_script],
                capture_output=True, text=True, timeout=1
            )
            app_name = res_app.stdout.strip()
            if not app_name:
                return ""

            # 2. If frontmost app is a browser, get active tab title (captures Azure blades)
            lower_app = app_name.lower()
            if "chrome" in lower_app:
                script = 'tell application "Google Chrome" to get title of active tab of front window'
                res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=1)
                if res.stdout.strip():
                    return res.stdout.strip()
            elif "safari" in lower_app:
                script = 'tell application "Safari" to get name of current tab of front window'
                res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=1)
                if res.stdout.strip():
                    return res.stdout.strip()
            elif "edge" in lower_app:
                script = 'tell application "Microsoft Edge" to get title of active tab of front window'
                res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=1)
                if res.stdout.strip():
                    return res.stdout.strip()
            elif "brave" in lower_app:
                script = 'tell application "Brave Browser" to get title of active tab of front window'
                res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=1)
                if res.stdout.strip():
                    return res.stdout.strip()

            # 3. Standard macOS window title fallback
            win_script = f'tell application "System Events" to tell process "{app_name}" to get name of front window'
            res_win = subprocess.run(
                ["osascript", "-e", win_script],
                capture_output=True, text=True, timeout=1
            )
            win_title = res_win.stdout.strip()
            return win_title if win_title else app_name
        except Exception:
            return ""

    # --- Linux Implementation ---
    else:
        try:
            res = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True, text=True, timeout=1
            )
            if res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return ""


def play_alert_sound(frequency: int = 1200, duration_ms: int = 400):
    """
    Plays an audible security alert sound across Windows, macOS, and Linux.
    """
    platform = sys.platform

    if platform == "win32":
        try:
            import winsound
            winsound.Beep(frequency, duration_ms)
        except Exception:
            pass
    elif platform == "darwin":
        try:
            # Native macOS alert sound
            ping_sound = "/System/Library/Sounds/Ping.aiff"
            if os.path.exists(ping_sound):
                subprocess.Popen(["afplay", ping_sound], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                print("\a", end="", flush=True)
        except Exception:
            print("\a", end="", flush=True)
    else:
        # Linux standard terminal bell or paplay
        print("\a", end="", flush=True)


def is_azure_active(title: str) -> bool:
    """
    Determines if the active window represents Microsoft Azure or an Azure blade.
    """
    if not title:
        return False
    keywords = ["azure", "portal.azure.com", "microsoft azure", "entra id", "virtual machine"]
    lower = title.lower()
    return any(k in lower for k in keywords)
