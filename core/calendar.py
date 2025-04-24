import os
import json
import datetime
import re
from datetime import datetime, timedelta

# Path to the calendar file
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CALENDAR_FILE = os.path.join(DATA_DIR, 'calendar.json')

# Ensure the data directory exists
try:
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
except Exception as e:
    print(f"Error creating data directory: {e}")

def load_events():
    """Load events from the JSON file"""
    if os.path.exists(CALENDAR_FILE):
        try:
            with open(CALENDAR_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, return an empty events list
            return []
    else:
        # If the file doesn't exist, create it with an empty list
        save_events([])
        return []

def save_events(events):
    """Save events to the JSON file"""
    with open(CALENDAR_FILE, 'w') as f:
        json.dump(events, f, indent=4)

def add_event(title, date_str, time_str=None, description=None, location=None):
    """Add a new event to the calendar"""
    events = load_events()
    
    # Parse date
    try:
        # Try different date formats
        date_formats = [
            "%Y-%m-%d",  # 2023-12-31
            "%d/%m/%Y",  # 31/12/2023
            "%m/%d/%Y",  # 12/31/2023
            "%d-%m-%Y",  # 31-12-2023
            "%B %d, %Y", # December 31, 2023
            "%d %B %Y",  # 31 December 2023
            "%A, %B %d", # Monday, December 31
            "today",     # today
            "tomorrow",  # tomorrow
            "next %A"    # next Monday
        ]
        
        event_date = None
        
        if date_str.lower() == "today":
            event_date = datetime.now().date()
        elif date_str.lower() == "tomorrow":
            event_date = (datetime.now() + timedelta(days=1)).date()
        elif date_str.lower().startswith("next "):
            # Handle "next Monday", "next Tuesday", etc.
            day_name = date_str.lower().split("next ")[1].strip()
            day_mapping = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6
            }
            if day_name in day_mapping:
                today = datetime.now()
                days_ahead = day_mapping[day_name] - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                event_date = (today + timedelta(days=days_ahead)).date()
        else:
            # Try the different date formats
            for fmt in date_formats:
                try:
                    if fmt.startswith("next"):
                        continue  # Skip the "next %A" format here
                    event_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
        
        if event_date is None:
            return f"Could not parse date: {date_str}. Please use a format like YYYY-MM-DD or 'today'."
        
        # Parse time if provided
        event_time = None
        if time_str:
            time_formats = [
                "%H:%M",      # 14:30
                "%I:%M %p",   # 2:30 PM
                "%I %p"       # 2 PM
            ]
            
            for fmt in time_formats:
                try:
                    event_time = datetime.strptime(time_str, fmt).time()
                    break
                except ValueError:
                    continue
            
            if event_time is None:
                return f"Could not parse time: {time_str}. Please use a format like HH:MM or H:MM AM/PM."
        
        # Create the event
        event = {
            "title": title,
            "date": event_date.strftime("%Y-%m-%d"),
            "id": len(events) + 1  # Simple ID generation
        }
        
        if event_time:
            event["time"] = event_time.strftime("%H:%M")
        if description:
            event["description"] = description
        if location:
            event["location"] = location
        
        events.append(event)
        save_events(events)
        
        date_display = event_date.strftime("%A, %B %d, %Y")
        time_display = f" at {event_time.strftime('%I:%M %p')}" if event_time else ""
        
        return f"Added event: {title} on {date_display}{time_display}"
        
    except Exception as e:
        return f"Error adding event: {e}"

def get_events_for_date(date_str):
    """Get all events for a specific date"""
    events = load_events()
    
    try:
        # Parse the date
        target_date = None
        
        if date_str.lower() == "today":
            target_date = datetime.now().date()
        elif date_str.lower() == "tomorrow":
            target_date = (datetime.now() + timedelta(days=1)).date()
        else:
            # Try different date formats
            date_formats = [
                "%Y-%m-%d",  # 2023-12-31
                "%d/%m/%Y",  # 31/12/2023
                "%m/%d/%Y",  # 12/31/2023
                "%d-%m-%Y",  # 31-12-2023
                "%B %d, %Y", # December 31, 2023
                "%d %B %Y",  # 31 December 2023
            ]
            
            for fmt in date_formats:
                try:
                    target_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
        
        if target_date is None:
            return f"Could not parse date: {date_str}. Please use a format like YYYY-MM-DD or 'today'."
        
        # Find events for the target date
        target_date_str = target_date.strftime("%Y-%m-%d")
        matching_events = [e for e in events if e["date"] == target_date_str]
        
        if not matching_events:
            date_display = target_date.strftime("%A, %B %d, %Y")
            return f"No events found for {date_display}."
        
        # Format the response
        date_display = target_date.strftime("%A, %B %d, %Y")
        result = f"Events for {date_display}:\n"
        
        for event in sorted(matching_events, key=lambda e: e.get("time", "00:00")):
            time_display = f" at {event['time']}" if "time" in event else ""
            result += f"- {event['title']}{time_display}"
            if "location" in event:
                result += f" at {event['location']}"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error retrieving events: {e}"

def delete_event(event_id=None, title=None, date_str=None):
    """Delete an event by ID or by title and date"""
    events = load_events()
    initial_count = len(events)
    
    try:
        if event_id:
            # Delete by ID
            events = [e for e in events if e.get("id") != event_id]
        elif title and date_str:
            # Parse the date
            target_date = None
            
            if date_str.lower() == "today":
                target_date = datetime.now().date()
            elif date_str.lower() == "tomorrow":
                target_date = (datetime.now() + timedelta(days=1)).date()
            else:
                # Try different date formats
                date_formats = [
                    "%Y-%m-%d",  # 2023-12-31
                    "%d/%m/%Y",  # 31/12/2023
                    "%m/%d/%Y",  # 12/31/2023
                    "%d-%m-%Y",  # 31-12-2023
                    "%B %d, %Y", # December 31, 2023
                    "%d %B %Y",  # 31 December 2023
                ]
                
                for fmt in date_formats:
                    try:
                        target_date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
            
            if target_date is None:
                return f"Could not parse date: {date_str}. Please use a format like YYYY-MM-DD or 'today'."
            
            # Find and delete events matching title and date
            target_date_str = target_date.strftime("%Y-%m-%d")
            events = [e for e in events if not (e["date"] == target_date_str and e["title"].lower() == title.lower())]
        else:
            return "Please provide either an event ID or both a title and date."
        
        if len(events) < initial_count:
            save_events(events)
            return "Event deleted successfully."
        else:
            return "No matching event found."
            
    except Exception as e:
        return f"Error deleting event: {e}"

def get_upcoming_events(days=7):
    """Get all events for the next X days"""
    events = load_events()
    
    try:
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        
        # Find events in the date range
        upcoming_events = []
        for event in events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if today <= event_date <= end_date:
                upcoming_events.append(event)
        
        if not upcoming_events:
            return f"No upcoming events for the next {days} days."
        
        # Format the response
        result = f"Upcoming events for the next {days} days:\n"
        
        # Group events by date
        events_by_date = {}
        for event in upcoming_events:
            event_date = event["date"]
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Sort dates and display events
        for date_str in sorted(events_by_date.keys()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_display = date_obj.strftime("%A, %B %d, %Y")
            result += f"\n{date_display}:\n"
            
            for event in sorted(events_by_date[date_str], key=lambda e: e.get("time", "00:00")):
                time_display = f" at {event['time']}" if "time" in event else ""
                result += f"- {event['title']}{time_display}"
                if "location" in event:
                    result += f" at {event['location']}"
                result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error retrieving upcoming events: {e}"

def parse_calendar_command(command):
    """Parse a natural language command to manage calendar events"""
    command = command.lower()
    
    # Add event
    add_match = re.search(r"add (?:an )?event(?: called| titled| named)? ([^,]+)(?:,| on| for) ([^,]+)(?:,| at)?(?: ([0-9:]+(?:\s*[ap]m)?))?(?: with description ([^,]+))?(?: at location ([^,]+))?", command, re.IGNORECASE)
    if add_match or "add event" in command:
        if add_match:
            title = add_match.group(1).strip()
            date_str = add_match.group(2).strip()
            time_str = add_match.group(3).strip() if add_match.group(3) else None
            description = add_match.group(4).strip() if add_match.group(4) else None
            location = add_match.group(5).strip() if add_match.group(5) else None
            
            return add_event(title, date_str, time_str, description, location)
        else:
            return "Please specify event details. For example: 'Add event called Meeting on tomorrow at 3pm'"
    
    # Get events for a date
    if "events for" in command or "what's on" in command or "what is on" in command or "appointments on" in command or "schedule for" in command:
        date_match = re.search(r"(?:events for|what's on|what is on|appointments on|schedule for) ([^?\.]+)", command, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(1).strip()
            return get_events_for_date(date_str)
    
    # Get upcoming events
    if "upcoming events" in command or "next events" in command or "show my calendar" in command:
        days_match = re.search(r"(?:for|next) ([0-9]+) days", command)
        days = int(days_match.group(1)) if days_match else 7
        return get_upcoming_events(days)
    
    # Delete event
    if "delete event" in command or "remove event" in command or "cancel event" in command:
        title_date_match = re.search(r"(?:delete|remove|cancel) event ([^,]+)(?:,| on| for) ([^,\.]+)", command, re.IGNORECASE)
        if title_date_match:
            title = title_date_match.group(1).strip()
            date_str = title_date_match.group(2).strip()
            return delete_event(title=title, date_str=date_str)
    
    return None