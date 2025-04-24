import os
import subprocess
import time
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32process
import psutil

# Windows API constants
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9

# Load user32.dll
user32 = ctypes.WinDLL('user32')

# Define function prototypes
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]

def get_active_window_title():
    """Get the title of the active window"""
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

def close_active_window():
    """Close the currently active window"""
    try:
        # Get the handle of the active window
        hwnd = user32.GetForegroundWindow()
        
        # Send a close message to the window
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        
        return True
    except Exception as e:
        print(f"Error closing active window: {e}")
        return False

def close_browser_tab():
    """Close the active browser tab"""
    try:
        # Simulate Ctrl+W keyboard shortcut
        subprocess.run(['powershell', '-command', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("^w")'])
        return True
    except Exception as e:
        print(f"Error closing browser tab: {e}")
        return False

def minimize_window():
    """Minimize the active window"""
    try:
        hwnd = user32.GetForegroundWindow()
        user32.ShowWindow(hwnd, SW_MINIMIZE)
        return True
    except Exception as e:
        print(f"Error minimizing window: {e}")
        return False

def maximize_window():
    """Maximize the active window"""
    try:
        hwnd = user32.GetForegroundWindow()
        user32.ShowWindow(hwnd, SW_MAXIMIZE)
        return True
    except Exception as e:
        print(f"Error maximizing window: {e}")
        return False

def restore_window():
    """Restore the active window"""
    try:
        hwnd = user32.GetForegroundWindow()
        user32.ShowWindow(hwnd, SW_RESTORE)
        return True
    except Exception as e:
        print(f"Error restoring window: {e}")
        return False

def switch_to_next_window():
    """Switch to the next window (Alt+Tab)"""
    try:
        subprocess.run(['powershell', '-command', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("%{TAB}")'])
        return True
    except Exception as e:
        print(f"Error switching windows: {e}")
        return False

def get_running_processes():
    """Get a list of running processes"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def kill_process_by_name(process_name):
    """Kill a process by name"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    except Exception as e:
        print(f"Error killing process: {e}")
        return False