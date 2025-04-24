"""
Test script for the new JARVIS features.
This script allows you to test the messaging, calling, contacts, calendar, and app-specific search features.
"""

from core.commands import run_command
from core.contacts import add_contact, list_contacts
from core.calendar import add_event, get_upcoming_events

def test_contacts():
    print("\n=== Testing Contacts ===")
    # Add a test contact
    print(add_contact("John Doe", "555-1234", "john@example.com", "555-1234"))
    print(add_contact("Jane Smith", "555-5678", "jane@example.com", "555-5678"))
    
    # List contacts
    print(list_contacts())
    
    # Test contact commands
    print(run_command("find contact named John"))
    print(run_command("list contacts"))

def test_messaging():
    print("\n=== Testing Messaging ===")
    # Test WhatsApp messaging (this will just show instructions, not actually send)
    print(run_command("send message to John on WhatsApp saying Hello, this is a test"))
    
    # Test email composition
    print(run_command("send email to john@example.com subject Test Email body This is a test email"))

def test_calling():
    print("\n=== Testing Calling ===")
    # Test WhatsApp calling (this will just show instructions, not actually call)
    print(run_command("call John on WhatsApp"))
    
    # Test video calling
    print(run_command("video call Jane on Teams"))

def test_calendar():
    print("\n=== Testing Calendar ===")
    # Add test events
    print(add_event("Team Meeting", "tomorrow", "14:00", "Weekly team sync", "Conference Room A"))
    print(add_event("Doctor Appointment", "next Monday", "10:30", "Annual checkup", "Medical Center"))
    
    # Test calendar commands
    print(run_command("what's on tomorrow"))
    print(run_command("show my upcoming events"))
    print(run_command("add event called Lunch with Client on Friday at 12:30"))

def test_app_search():
    print("\n=== Testing App-Specific Search ===")
    # Test searching in different apps
    print(run_command("search for budget in Google Drive"))
    print(run_command("search for Taylor Swift in Spotify"))
    print(run_command("search for Python tutorial in YouTube"))

def main():
    print("JARVIS New Features Test")
    print("=======================")
    
    test_contacts()
    test_messaging()
    test_calling()
    test_calendar()
    test_app_search()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()