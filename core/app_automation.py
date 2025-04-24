import os
import subprocess
import time
import pyautogui
import win32gui
import win32con
import win32process
import psutil
import re

# Set a small pause between PyAutoGUI commands for stability
pyautogui.PAUSE = 0.1

def find_window_by_title(title_pattern):
    """Find a window by its title using regex pattern matching"""
    result = []
    
    def enum_windows_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if re.search(title_pattern, window_title, re.IGNORECASE):
                results.append((hwnd, window_title))
    
    win32gui.EnumWindows(enum_windows_callback, result)
    return result

def activate_window(window_title):
    """Activate a window by its title"""
    try:
        windows = find_window_by_title(window_title)
        if windows:
            hwnd, actual_title = windows[0]
            win32gui.SetForegroundWindow(hwnd)
            return True
        return False
    except Exception as e:
        print(f"Error activating window: {e}")
        return False

def send_keys(keys):
    """Send keyboard input to the active window"""
    try:
        pyautogui.typewrite(keys)
        return True
    except Exception as e:
        print(f"Error sending keys: {e}")
        return False

def send_hotkey(*keys):
    """Send a hotkey combination to the active window"""
    try:
        pyautogui.hotkey(*keys)
        return True
    except Exception as e:
        print(f"Error sending hotkey: {e}")
        return False

def click_position(x, y):
    """Click at a specific position on the screen"""
    try:
        pyautogui.click(x, y)
        return True
    except Exception as e:
        print(f"Error clicking position: {e}")
        return False

def click_image(image_path, confidence=0.7):
    """Click on an image on the screen"""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            pyautogui.click(center)
            return True
        return False
    except Exception as e:
        print(f"Error clicking image: {e}")
        return False

def click_text(text, region=None):
    """Click on text on the screen (requires pytesseract)"""
    try:
        import pytesseract
        from PIL import ImageGrab
        
        # Take a screenshot
        if region:
            screenshot = ImageGrab.grab(region)
        else:
            screenshot = ImageGrab.grab()
        
        # Use OCR to find text
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        
        # Find the text
        for i, word in enumerate(data['text']):
            if text.lower() in word.lower():
                # Calculate the center of the word
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                
                # Click on the word
                pyautogui.click(x, y)
                return True
        
        return False
    except Exception as e:
        print(f"Error clicking text: {e}")
        return False

def drag_and_drop(start_x, start_y, end_x, end_y, duration=0.5):
    """Drag from one position to another"""
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=duration)
        pyautogui.mouseUp()
        return True
    except Exception as e:
        print(f"Error performing drag and drop: {e}")
        return False

def scroll(clicks, x=None, y=None):
    """Scroll the mouse wheel"""
    try:
        if x is not None and y is not None:
            pyautogui.moveTo(x, y)
        pyautogui.scroll(clicks)
        return True
    except Exception as e:
        print(f"Error scrolling: {e}")
        return False

def take_screenshot(output_path):
    """Take a screenshot and save it to a file"""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(output_path)
        return True
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return False

def get_screen_size():
    """Get the screen size"""
    try:
        width, height = pyautogui.size()
        return (width, height)
    except Exception as e:
        print(f"Error getting screen size: {e}")
        return None

def get_mouse_position():
    """Get the current mouse position"""
    try:
        x, y = pyautogui.position()
        return (x, y)
    except Exception as e:
        print(f"Error getting mouse position: {e}")
        return None

def wait_for_image(image_path, timeout=10, confidence=0.7):
    """Wait for an image to appear on the screen"""
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return True
            time.sleep(0.5)
        return False
    except Exception as e:
        print(f"Error waiting for image: {e}")
        return False

def wait_for_window(title_pattern, timeout=10):
    """Wait for a window to appear"""
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            windows = find_window_by_title(title_pattern)
            if windows:
                return True
            time.sleep(0.5)
        return False
    except Exception as e:
        print(f"Error waiting for window: {e}")
        return False

# Application-specific functions

def interact_with_browser(action, params=None):
    """Interact with a web browser"""
    browser_titles = ["Chrome", "Firefox", "Edge", "Internet Explorer", "Opera", "Safari"]
    
    # Try to find and activate a browser window
    for browser in browser_titles:
        if activate_window(browser):
            break
    else:
        return False
    
    # Perform the requested action
    if action == "new_tab":
        return send_hotkey("ctrl", "t")
    elif action == "close_tab":
        return send_hotkey("ctrl", "w")
    elif action == "next_tab":
        return send_hotkey("ctrl", "tab")
    elif action == "prev_tab":
        return send_hotkey("ctrl", "shift", "tab")
    elif action == "refresh":
        return send_hotkey("f5")
    elif action == "address_bar":
        return send_hotkey("ctrl", "l")
    elif action == "navigate":
        if params and "url" in params:
            send_hotkey("ctrl", "l")
            time.sleep(0.2)
            send_keys(params["url"])
            send_hotkey("enter")
            return True
    elif action == "search":
        if params and "query" in params:
            send_hotkey("ctrl", "l")
            time.sleep(0.2)
            send_keys(params["query"])
            send_hotkey("enter")
            return True
    
    return False

def interact_with_office(app, action, params=None):
    """Interact with Microsoft Office applications"""
    office_apps = {
        "word": "Word",
        "excel": "Excel",
        "powerpoint": "PowerPoint",
        "outlook": "Outlook"
    }
    
    if app not in office_apps:
        return False
    
    # Try to find and activate the Office app window
    if not activate_window(office_apps[app]):
        return False
    
    # Perform the requested action
    if action == "new_document":
        return send_hotkey("ctrl", "n")
    elif action == "open_document":
        return send_hotkey("ctrl", "o")
    elif action == "save":
        return send_hotkey("ctrl", "s")
    elif action == "save_as":
        return send_hotkey("f12")
    elif action == "print":
        return send_hotkey("ctrl", "p")
    elif action == "undo":
        return send_hotkey("ctrl", "z")
    elif action == "redo":
        return send_hotkey("ctrl", "y")
    elif action == "cut":
        return send_hotkey("ctrl", "x")
    elif action == "copy":
        return send_hotkey("ctrl", "c")
    elif action == "paste":
        return send_hotkey("ctrl", "v")
    elif action == "select_all":
        return send_hotkey("ctrl", "a")
    elif action == "bold":
        return send_hotkey("ctrl", "b")
    elif action == "italic":
        return send_hotkey("ctrl", "i")
    elif action == "underline":
        return send_hotkey("ctrl", "u")
    elif action == "type_text":
        if params and "text" in params:
            return send_keys(params["text"])
    
    return False

def interact_with_media_player(action, params=None):
    """Interact with media players (VLC, Windows Media Player, etc.)"""
    media_player_titles = ["VLC", "Windows Media Player", "Media Player", "Movies & TV"]
    
    # Try to find and activate a media player window
    for player in media_player_titles:
        if activate_window(player):
            break
    else:
        return False
    
    # Perform the requested action
    if action == "play_pause":
        return send_hotkey("space")
    elif action == "stop":
        return send_hotkey("s")
    elif action == "next":
        return send_hotkey("n")
    elif action == "previous":
        return send_hotkey("p")
    elif action == "volume_up":
        return send_hotkey("up")
    elif action == "volume_down":
        return send_hotkey("down")
    elif action == "mute":
        return send_hotkey("m")
    elif action == "fullscreen":
        return send_hotkey("f")
    
    return False

def interact_with_spotify(action, params=None):
    """Interact with Spotify"""
    if not activate_window("Spotify"):
        return False
    
    # Perform the requested action
    if action == "play_pause":
        return send_hotkey("space")
    elif action == "next_track":
        return send_hotkey("ctrl", "right")
    elif action == "previous_track":
        return send_hotkey("ctrl", "left")
    elif action == "volume_up":
        return send_hotkey("ctrl", "up")
    elif action == "volume_down":
        return send_hotkey("ctrl", "down")
    elif action == "search":
        if params and "query" in params:
            send_hotkey("ctrl", "l")
            time.sleep(0.2)
            send_keys(params["query"])
            send_hotkey("enter")
            return True
    
    return False