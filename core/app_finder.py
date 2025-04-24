import os
import winreg
import subprocess
import json
import re
from pathlib import Path

# Cache for storing discovered applications
app_cache = {}

def get_start_menu_programs():
    """Get a list of programs from the Start Menu"""
    programs = []
    
    # Common paths for Start Menu shortcuts
    start_menu_paths = [
        os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs")
    ]
    
    for start_menu_path in start_menu_paths:
        if os.path.exists(start_menu_path):
            for root, dirs, files in os.walk(start_menu_path):
                for file in files:
                    if file.endswith(".lnk"):
                        shortcut_path = os.path.join(root, file)
                        app_name = file[:-4]  # Remove .lnk extension
                        programs.append({
                            "name": app_name,
                            "path": shortcut_path,
                            "source": "start_menu"
                        })
    
    return programs

def get_installed_programs_from_registry():
    """Get a list of installed programs from the Windows Registry"""
    programs = []
    
    # Registry paths for installed programs
    registry_paths = [
        # HKLM paths
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        # HKCU paths
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        # App Paths (executable paths)
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths")
    ]
    
    for hkey, reg_path in registry_paths:
        try:
            registry_key = winreg.OpenKey(hkey, reg_path)
            
            for i in range(0, winreg.QueryInfoKey(registry_key)[0]):
                try:
                    subkey_name = winreg.EnumKey(registry_key, i)
                    subkey = winreg.OpenKey(registry_key, subkey_name)
                    
                    # For App Paths, the default value is the path to the executable
                    if "App Paths" in reg_path:
                        try:
                            exe_path = winreg.QueryValue(subkey, None)
                            if exe_path and exe_path.strip():
                                app_name = subkey_name
                                if app_name.lower().endswith(".exe"):
                                    app_name = app_name[:-4]  # Remove .exe extension
                                
                                programs.append({
                                    "name": app_name,
                                    "path": exe_path,
                                    "source": "app_paths"
                                })
                        except:
                            pass
                    else:
                        # For Uninstall keys, look for DisplayName and InstallLocation
                        try:
                            app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            
                            # Try to get the installation location
                            install_location = ""
                            try:
                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            except:
                                pass
                            
                            # Try to get the executable path
                            exe_path = ""
                            try:
                                exe_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                # DisplayIcon often contains the path to the executable with ,0 at the end
                                if exe_path and "," in exe_path:
                                    exe_path = exe_path.split(",")[0]
                            except:
                                pass
                            
                            # Use the executable path if available, otherwise use the install location
                            path = exe_path if exe_path else install_location
                            
                            programs.append({
                                "name": app_name,
                                "path": path,
                                "source": "registry"
                            })
                        except:
                            pass
                    
                    winreg.CloseKey(subkey)
                except Exception as e:
                    print(f"Error processing registry key: {e}")
            
            winreg.CloseKey(registry_key)
        except Exception as e:
            print(f"Error opening registry key {reg_path}: {e}")
    
    return programs

def get_common_program_paths():
    """Get paths for commonly used programs"""
    common_programs = {
        "chrome": [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ],
        "firefox": [
            "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
        ],
        "edge": [
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
        ],
        "word": [
            "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "C:\\Program Files\\Microsoft Office\\Office16\\WINWORD.EXE",
            "C:\\Program Files (x86)\\Microsoft Office\\Office16\\WINWORD.EXE"
        ],
        "excel": [
            "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "C:\\Program Files\\Microsoft Office\\Office16\\EXCEL.EXE",
            "C:\\Program Files (x86)\\Microsoft Office\\Office16\\EXCEL.EXE"
        ],
        "powerpoint": [
            "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
            "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
            "C:\\Program Files\\Microsoft Office\\Office16\\POWERPNT.EXE",
            "C:\\Program Files (x86)\\Microsoft Office\\Office16\\POWERPNT.EXE"
        ],
        "outlook": [
            "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
            "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
            "C:\\Program Files\\Microsoft Office\\Office16\\OUTLOOK.EXE",
            "C:\\Program Files (x86)\\Microsoft Office\\Office16\\OUTLOOK.EXE"
        ],
        "teams": [
            "C:\\Users\\prajw\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe",
            "C:\\Program Files\\Microsoft Teams\\current\\Teams.exe",
            "C:\\Program Files (x86)\\Microsoft Teams\\current\\Teams.exe"
        ],
        "spotify": [
            "C:\\Users\\prajw\\AppData\\Roaming\\Spotify\\Spotify.exe"
        ],
        "vlc": [
            "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"
        ],
        "notepad": [
            "C:\\Windows\\notepad.exe",
            "C:\\Windows\\System32\\notepad.exe"
        ],
        "vscode": [
            "C:\\Users\\prajw\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe"
        ],
        "photoshop": [
            "C:\\Program Files\\Adobe\\Adobe Photoshop 2023\\Photoshop.exe",
            "C:\\Program Files\\Adobe\\Adobe Photoshop CC 2023\\Photoshop.exe"
        ],
        "illustrator": [
            "C:\\Program Files\\Adobe\\Adobe Illustrator 2023\\Support Files\\Contents\\Windows\\Illustrator.exe",
            "C:\\Program Files\\Adobe\\Adobe Illustrator CC 2023\\Support Files\\Contents\\Windows\\Illustrator.exe"
        ],
        "premiere": [
            "C:\\Program Files\\Adobe\\Adobe Premiere Pro 2023\\Adobe Premiere Pro.exe",
            "C:\\Program Files\\Adobe\\Adobe Premiere Pro CC 2023\\Adobe Premiere Pro.exe"
        ],
        "aftereffects": [
            "C:\\Program Files\\Adobe\\Adobe After Effects 2023\\Support Files\\AfterFX.exe",
            "C:\\Program Files\\Adobe\\Adobe After Effects CC 2023\\Support Files\\AfterFX.exe"
        ],
        "steam": [
            "C:\\Program Files (x86)\\Steam\\steam.exe",
            "C:\\Program Files\\Steam\\steam.exe"
        ],
        "discord": [
            "C:\\Users\\prajw\\AppData\\Local\\Discord\\app-1.0.9013\\Discord.exe",
            "C:\\Users\\prajw\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe"
        ],
        "whatsapp": [
            "C:\\Program Files\\WindowsApps\\5319275A.WhatsAppDesktop_2.2318.2.0_x64__cv1g1gvanyjgm\\WhatsApp.exe",
            "C:\\Users\\prajw\\AppData\\Local\\WhatsApp\\WhatsApp.exe"
        ]
    }
    
    programs = []
    
    for app_name, paths in common_programs.items():
        for path in paths:
            if os.path.exists(path):
                programs.append({
                    "name": app_name,
                    "path": path,
                    "source": "common_paths"
                })
                break  # Only add the first valid path for each app
    
    return programs

def find_app_by_name(app_name):
    """Find an application by name"""
    # Convert to lowercase for case-insensitive matching
    app_name_lower = app_name.lower()
    
    # Check if the app is in the cache
    if app_name_lower in app_cache:
        return app_cache[app_name_lower]
    
    # Get all programs
    all_programs = []
    all_programs.extend(get_common_program_paths())
    all_programs.extend(get_start_menu_programs())
    all_programs.extend(get_installed_programs_from_registry())
    
    # Search for exact matches first
    for program in all_programs:
        if program["name"].lower() == app_name_lower:
            app_cache[app_name_lower] = program
            return program
    
    # Search for partial matches
    for program in all_programs:
        if app_name_lower in program["name"].lower():
            app_cache[app_name_lower] = program
            return program
    
    # Try to match common app name variations
    common_variations = {
        "chrome": ["google chrome", "chrome browser"],
        "firefox": ["mozilla firefox", "ff"],
        "edge": ["microsoft edge", "msedge"],
        "word": ["microsoft word", "ms word", "winword"],
        "excel": ["microsoft excel", "ms excel"],
        "powerpoint": ["microsoft powerpoint", "ms powerpoint", "ppt"],
        "outlook": ["microsoft outlook", "ms outlook"],
        "teams": ["microsoft teams", "ms teams"],
        "vscode": ["visual studio code", "vs code"],
        "explorer": ["file explorer", "windows explorer"],
        "cmd": ["command prompt", "command line", "terminal"],
        "powershell": ["windows powershell", "ps"],
        "notepad": ["windows notepad"],
        "paint": ["microsoft paint", "ms paint"],
        "calculator": ["windows calculator", "calc"],
        "spotify": ["spotify music"],
        "vlc": ["vlc media player", "videolan"],
        "photoshop": ["adobe photoshop", "ps"],
        "illustrator": ["adobe illustrator", "ai"],
        "premiere": ["adobe premiere", "premiere pro"],
        "aftereffects": ["adobe after effects", "ae"],
        "steam": ["steam client"],
        "discord": ["discord app"],
        "whatsapp": ["whatsapp desktop"]
    }
    
    for common_name, variations in common_variations.items():
        if app_name_lower == common_name or app_name_lower in variations:
            for program in all_programs:
                if program["name"].lower() == common_name:
                    app_cache[app_name_lower] = program
                    return program
    
    return None

def open_app(app_name):
    """Open an application by name"""
    app = find_app_by_name(app_name)
    
    if app:
        try:
            if app["source"] == "start_menu":
                # For .lnk files, use os.startfile
                os.startfile(app["path"])
            elif app["source"] == "registry" and app["path"]:
                # For registry entries with a path, try to find an executable
                for root, dirs, files in os.walk(app["path"]):
                    for file in files:
                        if file.endswith(".exe"):
                            os.startfile(os.path.join(root, file))
                            return True
                return False
            else:
                # For common paths, use os.startfile
                os.startfile(app["path"])
            return True
        except Exception as e:
            print(f"Error opening {app_name}: {e}")
            return False
    else:
        return False

def scan_for_executables(drive_letters=None):
    """Scan the system for executable files"""
    programs = []
    
    # If no drive letters are specified, use C: drive
    if not drive_letters:
        drive_letters = ['C:']
    
    # Common program directories to scan
    common_dirs = [
        "Program Files",
        "Program Files (x86)",
        "Windows\\System32",
        "Users\\prajw\\AppData\\Local",
        "Users\\prajw\\AppData\\Roaming",
        "ProgramData"
    ]
    
    # Skip these directories to avoid long scans
    skip_dirs = [
        "Windows\\WinSxS",
        "Windows\\assembly",
        "Windows\\Microsoft.NET",
        "Windows\\SoftwareDistribution",
        "$Recycle.Bin",
        "System Volume Information"
    ]
    
    for drive in drive_letters:
        for common_dir in common_dirs:
            root_dir = os.path.join(drive, common_dir)
            if os.path.exists(root_dir):
                print(f"Scanning {root_dir} for executables...")
                
                for root, dirs, files in os.walk(root_dir):
                    # Skip directories that match any in skip_dirs
                    if any(skip_dir in root for skip_dir in skip_dirs):
                        continue
                    
                    for file in files:
                        if file.lower().endswith(".exe"):
                            exe_path = os.path.join(root, file)
                            app_name = file[:-4]  # Remove .exe extension
                            
                            programs.append({
                                "name": app_name,
                                "path": exe_path,
                                "source": "scan"
                            })
    
    return programs

def get_installed_apps_list():
    """Get a list of all installed applications"""
    all_programs = []
    
    # Get programs from various sources
    all_programs.extend(get_common_program_paths())
    all_programs.extend(get_start_menu_programs())
    all_programs.extend(get_installed_programs_from_registry())
    
    # Optionally scan for executables (this can be slow)
    # Uncomment the next line to enable full system scanning
    # all_programs.extend(scan_for_executables())
    
    # Remove duplicates
    unique_programs = []
    seen_names = set()
    
    for program in all_programs:
        if program["name"].lower() not in seen_names:
            unique_programs.append(program)
            seen_names.add(program["name"].lower())
    
    return unique_programs

# Initialize the cache with common program paths
def init_cache():
    common_programs = get_common_program_paths()
    for program in common_programs:
        app_cache[program["name"].lower()] = program

# Initialize the cache when the module is imported
init_cache()