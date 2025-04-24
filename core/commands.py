import os
import subprocess
import webbrowser
import re
import time
from core.app_finder import open_app, get_installed_apps_list
from core.music_player import play_music, play_spotify_song, play_youtube_music
from core.system_control import (
    close_active_window, close_browser_tab, minimize_window, 
    maximize_window, restore_window, switch_to_next_window,
    get_active_window_title, kill_process_by_name
)
from core.app_automation import (
    activate_window, send_keys, send_hotkey, click_position,
    interact_with_browser, interact_with_office, interact_with_media_player,
    interact_with_spotify
)
from core.contacts import parse_contact_command, find_contact
from core.calendar import parse_calendar_command

def run_command(command):
    command = command.lower()
    
    # Function to record successful command execution
    def record_success(response):
        try:
            from core.self_training import record_interaction
            record_interaction(command, response, was_successful=True)
        except Exception as e:
            print(f"Error recording interaction: {e}")
        return response

    # App Control - Generic app opening
    open_app_match = re.search(r"open\s+(?:the\s+)?(?:app|application)?\s*['\"]?([^'\"]+)['\"]?", command, re.IGNORECASE)
    if open_app_match:
        app_name = open_app_match.group(1).strip()
        
        # Skip if it's a website (will be handled by website control)
        if not any(site in app_name for site in ["youtube", "google", "github", "gmail", "maps"]):
            if open_app(app_name):
                return record_success(f"Opening {app_name}.")
    
    # Specific app opening commands (for backward compatibility)
    if "open chrome" in command:
        if open_app("chrome"):
            return record_success("Opening Chrome.")
        else:
            os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
            return record_success("Opening Chrome.")
    elif "open vscode" in command or "open vs code" in command:
        if open_app("vscode"):
            return record_success("Opening Visual Studio Code.")
        else:
            subprocess.Popen(["code"])
            return record_success("Opening Visual Studio Code.")
    elif "open notepad" in command:
        if open_app("notepad"):
            return "Opening Notepad."
        else:
            os.system("notepad")
            return "Opening Notepad."
    elif "open cmd" in command or "open command prompt" in command:
        if open_app("cmd"):
            return "Opening Command Prompt."
        else:
            os.system("start cmd")
            return "Opening Command Prompt."
    elif "open whatsapp" in command:
        if open_app("whatsapp"):
            return "Opening WhatsApp."
        else:
            try:
                # Try to open WhatsApp desktop app if installed
                os.startfile("C:\\Program Files\\WindowsApps\\5319275A.WhatsAppDesktop_2.2318.2.0_x64__cv1g1gvanyjgm\\WhatsApp.exe")
                return "Opening WhatsApp."
            except:
                # If desktop app not found, open WhatsApp Web
                webbrowser.open("https://web.whatsapp.com")
                return "Opening WhatsApp Web."
    elif "open spotify" in command:
        if open_app("spotify"):
            return "Opening Spotify."
        else:
            try:
                os.startfile("C:\\Users\\prajw\\AppData\\Roaming\\Spotify\\Spotify.exe")
                return "Opening Spotify."
            except:
                webbrowser.open("https://open.spotify.com")
                return "Opening Spotify Web."
    elif "open word" in command or "open microsoft word" in command:
        if open_app("word"):
            return "Opening Microsoft Word."
        else:
            try:
                os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE")
                return "Opening Microsoft Word."
            except:
                return "Could not find Microsoft Word."
    elif "open excel" in command or "open microsoft excel" in command:
        if open_app("excel"):
            return "Opening Microsoft Excel."
        else:
            try:
                os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE")
                return "Opening Microsoft Excel."
            except:
                return "Could not find Microsoft Excel."
    elif "open teams" in command or "open microsoft teams" in command:
        if open_app("teams"):
            return "Opening Microsoft Teams."
        else:
            try:
                # Try different possible paths for Microsoft Teams
                possible_paths = [
                    "C:\\Users\\prajw\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe",
                    "C:\\Program Files\\Microsoft Teams\\current\\Teams.exe",
                    "C:\\Program Files (x86)\\Microsoft Teams\\current\\Teams.exe",
                    "C:\\Users\\prajw\\AppData\\Local\\Microsoft\\Teams\\Update.exe",
                    "C:\\Users\\prajw\\AppData\\Local\\Microsoft\\TeamsMeetingAddin\\1.0.23073.1\\x64\\Microsoft.Teams.MeetingAddin.dll"
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        os.startfile(path)
                        return "Opening Microsoft Teams."
                
                # If no desktop app is found, open Teams web
                webbrowser.open("https://teams.microsoft.com")
                return "Opening Microsoft Teams in your browser."
            except:
                # Fallback to web version
                webbrowser.open("https://teams.microsoft.com")
                return "Opening Microsoft Teams in your browser."

    # Website Control
    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
        return record_success("Opening YouTube.")
    elif "open google" in command:
        webbrowser.open("https://google.com")
        return record_success("Opening Google.")
    elif "open github" in command:
        webbrowser.open("https://github.com")
        return record_success("Opening GitHub.")
    elif "open gmail" in command:
        webbrowser.open("https://mail.google.com")
        return record_success("Opening Gmail.")
    elif "open maps" in command or "open google maps" in command:
        webbrowser.open("https://maps.google.com")
        return record_success("Opening Google Maps.")
        
    # System Commands
    elif "shutdown" in command or "shut down" in command:
        os.system("shutdown /s /t 60")
        return "Shutting down the computer in 60 seconds. Say 'cancel shutdown' to abort."
    elif "cancel shutdown" in command:
        os.system("shutdown /a")
        return "Shutdown aborted."
    elif "restart" in command or "reboot" in command:
        os.system("shutdown /r /t 60")
        return "Restarting the computer in 60 seconds. Say 'cancel restart' to abort."
    elif "cancel restart" in command:
        os.system("shutdown /a")
        return "Restart aborted."
    elif "sleep" in command and "computer" in command:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Putting the computer to sleep."

    # Music Commands
    elif "play" in command:
        # Check if it's a music-related command
        if any(word in command for word in ["music", "song", "track", "album", "artist", "playlist"]):
            return play_music(command)
        # If it's just "play X", assume it's a song
        else:
            song_match = re.search(r"play\s+([^,\.]+)", command, re.IGNORECASE)
            if song_match:
                song_name = song_match.group(1).strip()
                if "on spotify" in command.lower():
                    return play_spotify_song(song_name)
                elif "on youtube" in command.lower():
                    return play_youtube_music(song_name)
                else:
                    return play_spotify_song(song_name)
    
    # Search Commands
    elif "search for" in command or "google" in command:
        search_query = ""
        if "search for" in command:
            search_query = command.split("search for")[-1].strip()
        elif "google" in command:
            search_query = command.split("google")[-1].strip()
        
        if search_query:
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching for '{search_query}'"
    
    elif "youtube search" in command or "search youtube" in command or "search on youtube" in command:
        search_query = ""
        if "youtube search" in command:
            search_query = command.split("youtube search")[-1].strip()
        elif "search youtube" in command:
            search_query = command.split("search youtube")[-1].strip()
        elif "search on youtube" in command:
            search_query = command.split("search on youtube")[-1].strip()
        
        if search_query:
            search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching YouTube for '{search_query}'"

    # Window Control
    elif "close window" in command or "close this window" in command or "close the window" in command:
        window_title = get_active_window_title()
        if close_active_window():
            return f"Closing window: {window_title}"
        else:
            return "Could not close the window."
    elif "close tab" in command or "close this tab" in command or "close the tab" in command:
        if close_browser_tab():
            return "Closing the current browser tab."
        else:
            return "Could not close the browser tab."
    elif "minimize window" in command or "minimize this window" in command:
        window_title = get_active_window_title()
        if minimize_window():
            return f"Minimizing window: {window_title}"
        else:
            return "Could not minimize the window."
    elif "maximize window" in command or "maximize this window" in command:
        window_title = get_active_window_title()
        if maximize_window():
            return f"Maximizing window: {window_title}"
        else:
            return "Could not maximize the window."
    elif "switch window" in command or "switch to next window" in command or "alt tab" in command:
        if switch_to_next_window():
            return "Switching to the next window."
        else:
            return "Could not switch windows."
    
    # Advanced App Interaction - Browser
    elif "new tab" in command:
        if interact_with_browser("new_tab"):
            return "Opening a new browser tab."
        else:
            return "Could not open a new browser tab."
    elif "next tab" in command:
        if interact_with_browser("next_tab"):
            return "Switching to the next browser tab."
        else:
            return "Could not switch browser tabs."
    elif "previous tab" in command:
        if interact_with_browser("prev_tab"):
            return "Switching to the previous browser tab."
        else:
            return "Could not switch browser tabs."
    elif "refresh page" in command or "reload page" in command:
        if interact_with_browser("refresh"):
            return "Refreshing the current page."
        else:
            return "Could not refresh the page."
    elif "go to address bar" in command:
        if interact_with_browser("address_bar"):
            return "Focusing on the address bar."
        else:
            return "Could not focus on the address bar."
    
    # Advanced App Interaction - Office
    elif "new document" in command:
        if "word" in command and interact_with_office("word", "new_document"):
            return "Creating a new Word document."
        elif "excel" in command and interact_with_office("excel", "new_document"):
            return "Creating a new Excel spreadsheet."
        elif "powerpoint" in command and interact_with_office("powerpoint", "new_document"):
            return "Creating a new PowerPoint presentation."
        else:
            return "Could not create a new document."
    elif "save document" in command or "save file" in command:
        if "word" in command and interact_with_office("word", "save"):
            return "Saving the Word document."
        elif "excel" in command and interact_with_office("excel", "save"):
            return "Saving the Excel spreadsheet."
        elif "powerpoint" in command and interact_with_office("powerpoint", "save"):
            return "Saving the PowerPoint presentation."
        else:
            # Try to send Ctrl+S to the active window
            if send_hotkey("ctrl", "s"):
                return "Saving the current document."
            else:
                return "Could not save the document."
    
    # Advanced App Interaction - Media Players
    elif "pause" in command or "play" in command:
        if "spotify" in command and interact_with_spotify("play_pause"):
            return "Playing/pausing Spotify."
        elif interact_with_media_player("play_pause"):
            return "Playing/pausing media."
        else:
            # Try to send space key to the active window
            if send_keys(" "):
                return "Sending play/pause command."
            else:
                return "Could not control playback."
    elif "next track" in command or "next song" in command:
        if "spotify" in command and interact_with_spotify("next_track"):
            return "Playing the next track on Spotify."
        elif interact_with_media_player("next"):
            return "Playing the next track."
        else:
            return "Could not play the next track."
    elif "previous track" in command or "previous song" in command:
        if "spotify" in command and interact_with_spotify("previous_track"):
            return "Playing the previous track on Spotify."
        elif interact_with_media_player("previous"):
            return "Playing the previous track."
        else:
            return "Could not play the previous track."
    elif "volume up" in command:
        if "spotify" in command and interact_with_spotify("volume_up"):
            return "Increasing Spotify volume."
        elif interact_with_media_player("volume_up"):
            return "Increasing volume."
        else:
            return "Could not increase volume."
    elif "volume down" in command:
        if "spotify" in command and interact_with_spotify("volume_down"):
            return "Decreasing Spotify volume."
        elif interact_with_media_player("volume_down"):
            return "Decreasing volume."
        else:
            return "Could not decrease volume."
    
    # Text Input
    elif "type" in command:
        text_match = re.search(r"type\s+['\"]?([^'\"]+)['\"]?", command, re.IGNORECASE)
        if text_match:
            text_to_type = text_match.group(1).strip()
            if send_keys(text_to_type):
                return f"Typing: {text_to_type}"
            else:
                return "Could not type the text."
    
    # Generic Keyboard Shortcuts
    elif "copy" in command:
        if send_hotkey("ctrl", "c"):
            return "Copying selected content."
        else:
            return "Could not copy content."
    elif "paste" in command:
        if send_hotkey("ctrl", "v"):
            return "Pasting content."
        else:
            return "Could not paste content."
    elif "cut" in command:
        if send_hotkey("ctrl", "x"):
            return "Cutting selected content."
        else:
            return "Could not cut content."
    elif "select all" in command:
        if send_hotkey("ctrl", "a"):
            return "Selecting all content."
        else:
            return "Could not select content."
    elif "undo" in command:
        if send_hotkey("ctrl", "z"):
            return "Undoing the last action."
        else:
            return "Could not undo the action."
    elif "redo" in command:
        if send_hotkey("ctrl", "y"):
            return "Redoing the action."
        else:
            return "Could not redo the action."
    
    # Special Keys
    elif "press enter" in command:
        if send_keys("\n"):
            return "Pressing Enter."
        else:
            return "Could not press Enter."
    elif "press tab" in command:
        if send_keys("\t"):
            return "Pressing Tab."
        else:
            return "Could not press Tab."
    elif "press escape" in command or "press esc" in command:
        if send_hotkey("escape"):
            return "Pressing Escape."
        else:
            return "Could not press Escape."
    elif "press space" in command:
        if send_keys(" "):
            return "Pressing Space."
        else:
            return "Could not press Space."
    elif "press backspace" in command:
        if send_hotkey("backspace"):
            return "Pressing Backspace."
        else:
            return "Could not press Backspace."
    elif "press delete" in command:
        if send_hotkey("delete"):
            return "Pressing Delete."
        else:
            return "Could not press Delete."
    elif "press up" in command:
        if send_hotkey("up"):
            return "Pressing Up arrow."
        else:
            return "Could not press Up arrow."
    elif "press down" in command:
        if send_hotkey("down"):
            return "Pressing Down arrow."
        else:
            return "Could not press Down arrow."
    elif "press left" in command:
        if send_hotkey("left"):
            return "Pressing Left arrow."
        else:
            return "Could not press Left arrow."
    elif "press right" in command:
        if send_hotkey("right"):
            return "Pressing Right arrow."
        else:
            return "Could not press Right arrow."
    
    # System Information
    elif "list apps" in command or "show installed apps" in command or "what apps do i have" in command:
        apps = get_installed_apps_list()
        app_names = [app["name"] for app in apps[:20]]  # Limit to 20 apps to avoid too long response
        return f"Here are some of your installed applications: {', '.join(app_names)}. You can ask me to open any of these."
    elif "what window is this" in command or "what is this window" in command or "what window am i in" in command:
        window_title = get_active_window_title()
        return f"You are currently in: {window_title}"
    
    # Contact Management
    contact_response = parse_contact_command(command)
    if contact_response:
        return record_success(contact_response)
    
    # Calendar Management
    calendar_response = parse_calendar_command(command)
    if calendar_response:
        return record_success(calendar_response)
    
    # Messaging functionality
    messaging_response = handle_messaging_commands(command)
    if messaging_response:
        return record_success(messaging_response)
        
    # Calling functionality
    calling_response = handle_calling_commands(command)
    if calling_response:
        return record_success(calling_response)
        
    # App-specific search
    app_search_response = handle_app_search_commands(command)
    if app_search_response:
        return record_success(app_search_response)
    
    # File System
    file_response = handle_file_commands(command)
    if file_response:
        return record_success(file_response)

    return None


def handle_messaging_commands(command):
    # WhatsApp messaging
    if "send message" in command and "whatsapp" in command:
        # Extract recipient and message
        try:
            # Pattern: "send message to [recipient] on whatsapp saying [message]"
            if "to" in command and "saying" in command:
                recipient_name = command.split("to")[1].split("on whatsapp")[0].strip()
                message = command.split("saying")[1].strip()
                
                # Try to find the contact in our contacts database
                contact = find_contact(recipient_name)
                if contact and 'whatsapp' in contact:
                    recipient = contact['name']  # Use the proper name from contacts
                else:
                    recipient = recipient_name  # Use the name as provided in the command
                
                # Open WhatsApp
                if open_app("whatsapp"):
                    time.sleep(2)  # Wait for WhatsApp to open
                    
                    # Search for contact
                    send_hotkey("ctrl", "f")  # Search shortcut in WhatsApp
                    time.sleep(0.5)
                    send_keys(recipient)
                    time.sleep(1)
                    send_hotkey("enter")
                    time.sleep(1)
                    
                    # Type and send message
                    send_keys(message)
                    time.sleep(0.5)
                    send_hotkey("enter")
                    
                    return f"Message sent to {recipient} on WhatsApp."
                else:
                    # Try to open WhatsApp Web
                    webbrowser.open("https://web.whatsapp.com")
                    time.sleep(5)  # Wait for WhatsApp Web to load
                    return f"Please manually search for {recipient} and send the message: {message}"
            else:
                return "Please specify the recipient and message. For example: 'Send message to John on WhatsApp saying Hello'"
        except Exception as e:
            return f"Could not send WhatsApp message. Error: {e}"
    
    # SMS messaging
    elif "send sms" in command or ("send message" in command and "sms" in command):
        try:
            if "to" in command and "saying" in command:
                recipient = command.split("to")[1].split("saying")[0].strip()
                message = command.split("saying")[1].strip()
                
                # On Windows, we can open the Messages app
                if open_app("messages"):
                    time.sleep(2)
                    # The rest would depend on the specific SMS app interface
                    return f"Messages app opened. Please manually send SMS to {recipient} with message: {message}"
                else:
                    return "Could not open Messages app. Please make sure it's installed."
            else:
                return "Please specify the recipient and message. For example: 'Send SMS to John saying Hello'"
        except Exception as e:
            return f"Could not send SMS. Error: {e}"
    
    # Email messaging
    elif "send email" in command or "compose email" in command:
        try:
            if "to" in command and "subject" in command and "body" in command:
                recipient = command.split("to")[1].split("subject")[0].strip()
                subject = command.split("subject")[1].split("body")[0].strip()
                body = command.split("body")[1].strip()
                
                # Create a mailto URL
                mailto_url = f"mailto:{recipient}?subject={subject}&body={body}"
                webbrowser.open(mailto_url)
                return f"Composing email to {recipient}"
            else:
                return "Please specify recipient, subject, and body. For example: 'Send email to john@example.com subject Meeting body Let's meet tomorrow'"
        except Exception as e:
            return f"Could not compose email. Error: {e}"
    
    return None


def handle_calling_commands(command):
    # Voice calls via WhatsApp
    if "call" in command and "whatsapp" in command:
        try:
            # Extract contact name
            contact_name = command.split("call")[1].split("on whatsapp")[0].strip()
            
            # Try to find the contact in our contacts database
            contact_info = find_contact(contact_name)
            if contact_info:
                contact_name = contact_info['name']  # Use the proper name from contacts
            
            # Open WhatsApp
            if open_app("whatsapp"):
                time.sleep(2)  # Wait for WhatsApp to open
                
                # Search for contact
                send_hotkey("ctrl", "f")  # Search shortcut in WhatsApp
                time.sleep(0.5)
                send_keys(contact_name)
                time.sleep(1)
                send_hotkey("enter")
                time.sleep(1)
                
                # Click on call button (this would need to be customized based on screen position)
                # For now, we'll just provide instructions
                return f"WhatsApp opened with {contact_name}. Please click the call button manually."
            else:
                # Try to open WhatsApp Web
                webbrowser.open("https://web.whatsapp.com")
                time.sleep(5)
                return f"Please manually search for {contact_name} and initiate the call."
        except Exception as e:
            return f"Could not initiate WhatsApp call. Error: {e}"
    
    # Regular phone calls (using default phone app)
    elif "call" in command and any(word in command for word in ["phone", "mobile", "cell"]):
        try:
            # Extract contact name or number
            if "phone" in command:
                contact = command.split("call")[1].split("on phone")[0].strip()
            elif "mobile" in command:
                contact = command.split("call")[1].split("on mobile")[0].strip()
            elif "cell" in command:
                contact = command.split("call")[1].split("on cell")[0].strip()
            else:
                contact = command.split("call")[1].strip()
            
            # Try to open the Phone app (Windows Your Phone app)
            if open_app("your phone") or open_app("phone"):
                time.sleep(2)
                return f"Phone app opened. Please manually call {contact}."
            else:
                return "Could not open Phone app. Please make sure it's installed."
        except Exception as e:
            return f"Could not initiate phone call. Error: {e}"
    
    # Video calls
    elif "video call" in command:
        try:
            contact = command.split("video call")[1].strip()
            
            # Try different video calling apps
            if "teams" in command and (open_app("teams") or open_app("microsoft teams")):
                time.sleep(2)
                return f"Microsoft Teams opened. Please manually start a video call with {contact}."
            elif "zoom" in command and open_app("zoom"):
                time.sleep(2)
                return f"Zoom opened. Please manually start a video call with {contact}."
            elif "skype" in command and open_app("skype"):
                time.sleep(2)
                return f"Skype opened. Please manually start a video call with {contact}."
            elif "whatsapp" in command:
                if open_app("whatsapp"):
                    time.sleep(2)
                    send_hotkey("ctrl", "f")
                    time.sleep(0.5)
                    send_keys(contact)
                    time.sleep(1)
                    send_hotkey("enter")
                    time.sleep(1)
                    return f"WhatsApp opened with {contact}. Please click the video call button manually."
                else:
                    webbrowser.open("https://web.whatsapp.com")
                    time.sleep(5)
                    return f"Please manually search for {contact} and initiate the video call."
            else:
                # Default to Teams
                if open_app("teams") or open_app("microsoft teams"):
                    time.sleep(2)
                    return f"Microsoft Teams opened. Please manually start a video call with {contact}."
                else:
                    return "Could not find a suitable video calling app. Please specify which app to use."
        except Exception as e:
            return f"Could not initiate video call. Error: {e}"
    
    return None


def handle_app_search_commands(command):
    # Search in specific apps
    if "search" in command and "in" in command:
        try:
            # Extract search query and app name
            search_query = command.split("search")[1].split("in")[0].strip()
            app_name = command.split("in")[1].strip()
            
            # Search in different apps
            if "spotify" in app_name:
                if open_app("spotify"):
                    time.sleep(2)
                    send_hotkey("ctrl", "l")  # Focus on search in Spotify
                    time.sleep(0.5)
                    send_keys(search_query)
                    time.sleep(0.5)
                    send_hotkey("enter")
                    return f"Searching for '{search_query}' in Spotify."
                else:
                    webbrowser.open(f"https://open.spotify.com/search/{search_query.replace(' ', '%20')}")
                    return f"Searching for '{search_query}' in Spotify Web."
            
            elif "youtube" in app_name:
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}")
                return f"Searching for '{search_query}' on YouTube."
            
            elif "netflix" in app_name:
                webbrowser.open(f"https://www.netflix.com/search?q={search_query.replace(' ', '%20')}")
                return f"Searching for '{search_query}' on Netflix."
            
            elif "amazon" in app_name:
                webbrowser.open(f"https://www.amazon.com/s?k={search_query.replace(' ', '+')}")
                return f"Searching for '{search_query}' on Amazon."
            
            elif "google drive" in app_name or "drive" in app_name:
                webbrowser.open(f"https://drive.google.com/drive/search?q={search_query.replace(' ', '%20')}")
                return f"Searching for '{search_query}' in Google Drive."
            
            elif "gmail" in app_name:
                webbrowser.open(f"https://mail.google.com/mail/u/0/#search/{search_query.replace(' ', '%20')}")
                return f"Searching for '{search_query}' in Gmail."
            
            elif "file explorer" in app_name or "files" in app_name:
                if open_app("explorer") or os.system("explorer") == 0:
                    time.sleep(1)
                    send_hotkey("f3")  # Search in File Explorer
                    time.sleep(0.5)
                    send_keys(search_query)
                    time.sleep(0.5)
                    send_hotkey("enter")
                    return f"Searching for '{search_query}' in File Explorer."
                else:
                    return "Could not open File Explorer."
            
            else:
                # Generic app search - open the app and try to use Ctrl+F
                if open_app(app_name):
                    time.sleep(2)
                    send_hotkey("ctrl", "f")
                    time.sleep(0.5)
                    send_keys(search_query)
                    time.sleep(0.5)
                    send_hotkey("enter")
                    return f"Searching for '{search_query}' in {app_name}."
                else:
                    return f"Could not open {app_name}."
        
        except Exception as e:
            return f"Could not perform search. Error: {e}"
    
    # Perform actions in specific apps
    elif "in" in command and any(action in command for action in ["open", "create", "edit", "delete", "share"]):
        try:
            # Extract action and app name
            action = next(act for act in ["open", "create", "edit", "delete", "share"] if act in command)
            app_name = command.split("in")[1].strip()
            
            # Extract item name if available
            item_name = ""
            if action in command and action + " " in command:
                item_name = command.split(action)[1].split("in")[0].strip()
            
            # Handle different apps and actions
            if "google docs" in app_name or "docs" in app_name:
                if action == "create":
                    webbrowser.open("https://docs.google.com/document/create")
                    return "Creating a new Google Doc."
                elif action == "open" and item_name:
                    webbrowser.open(f"https://docs.google.com/document/u/0/?q={item_name.replace(' ', '%20')}")
                    return f"Searching for '{item_name}' in Google Docs."
                else:
                    webbrowser.open("https://docs.google.com/document/u/0/")
                    return "Opening Google Docs."
            
            elif "google sheets" in app_name or "sheets" in app_name:
                if action == "create":
                    webbrowser.open("https://sheets.google.com/create")
                    return "Creating a new Google Sheet."
                elif action == "open" and item_name:
                    webbrowser.open(f"https://sheets.google.com/u/0/?q={item_name.replace(' ', '%20')}")
                    return f"Searching for '{item_name}' in Google Sheets."
                else:
                    webbrowser.open("https://sheets.google.com/u/0/")
                    return "Opening Google Sheets."
            
            elif "word" in app_name:
                if action == "create":
                    if open_app("word"):
                        time.sleep(2)
                        # Word usually opens with a new document
                        return "Creating a new Word document."
                    else:
                        return "Could not open Microsoft Word."
                elif action == "open" and item_name:
                    if open_app("word"):
                        time.sleep(2)
                        send_hotkey("ctrl", "o")  # Open file dialog
                        time.sleep(1)
                        send_keys(item_name)
                        time.sleep(0.5)
                        send_hotkey("enter")
                        return f"Attempting to open '{item_name}' in Word."
                    else:
                        return "Could not open Microsoft Word."
                else:
                    if open_app("word"):
                        return "Opening Microsoft Word."
                    else:
                        return "Could not open Microsoft Word."
            
            # Add more apps as needed
            
            else:
                if open_app(app_name):
                    return f"Opened {app_name}. Please manually {action} {item_name}."
                else:
                    return f"Could not open {app_name}."
        
        except Exception as e:
            return f"Could not perform action in app. Error: {e}"
    
    return None


def handle_file_commands(command):
    base_path = os.path.expanduser("~")  # Your user directory (like C:/Users/Prajwal)

    if "create folder" in command:
        try:
            folder_name = command.split("create folder named")[-1].strip()
            path = os.path.join(base_path, folder_name)
            os.makedirs(path, exist_ok=True)
            return f"Folder '{folder_name}' created."
        except Exception as e:
            return f"Could not create folder. Error: {e}"

    elif "delete file" in command:
        try:
            file_name = command.split("delete file named")[-1].strip()
            file_path = os.path.join(base_path, file_name)
            os.remove(file_path)
            return f"File '{file_name}' deleted."
        except FileNotFoundError:
            return f"File '{file_name}' not found."
        except Exception as e:
            return f"Could not delete file. Error: {e}"

    elif "list files in" in command:
        try:
            folder_name = command.split("list files in")[-1].strip()
            folder_path = os.path.join(base_path, folder_name)
            files = os.listdir(folder_path)
            return f"Files in {folder_name}: {', '.join(files)}"
        except Exception as e:
            return f"Could not list files. Error: {e}"
    else:
        return None
