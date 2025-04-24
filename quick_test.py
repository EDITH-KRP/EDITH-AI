"""
Quick test script for JARVIS features.
"""

import os
import sys

def test_contacts():
    print("\n=== Testing Contacts ===")
    try:
        from core.contacts import add_contact, list_contacts, find_contact
        
        # Add contacts
        print(add_contact("John Doe", "555-1234", "john@example.com", "555-1234"))
        print(add_contact("Jane Smith", "555-5678", "jane@example.com", "555-5678"))
        
        # List contacts
        print("All contacts:")
        print(list_contacts())
        
        # Find contact
        print("Finding John:")
        print(find_contact("John"))
        
        return True
    except Exception as e:
        print(f"Error testing contacts: {e}")
        return False

def test_calendar():
    print("\n=== Testing Calendar ===")
    try:
        from core.calendar import add_event, get_upcoming_events, get_events_for_date
        
        # Add events
        print(add_event("Team Meeting", "tomorrow", "14:00", "Weekly team sync", "Conference Room A"))
        print(add_event("Doctor Appointment", "next Monday", "10:30", "Annual checkup", "Medical Center"))
        
        # Get upcoming events
        print("Upcoming events:")
        print(get_upcoming_events())
        
        # Get events for tomorrow
        print("Tomorrow's events:")
        print(get_events_for_date("tomorrow"))
        
        return True
    except Exception as e:
        print(f"Error testing calendar: {e}")
        return False

def test_commands():
    print("\n=== Testing Commands ===")
    try:
        from core.commands import run_command
        
        # Test various commands
        commands = [
            "what can you do",
            "open chrome",
            "search for Python tutorials",
            "what's the weather like today",
            "add contact named Test User with phone 555-9999 email test@example.com",
            "add event called Test Event on tomorrow at 15:00",
            "show my upcoming events"
        ]
        
        for cmd in commands:
            print(f"\nCommand: {cmd}")
            response = run_command(cmd)
            print(f"Response: {response}")
        
        return True
    except Exception as e:
        print(f"Error testing commands: {e}")
        return False

def test_self_training():
    print("\n=== Testing Self-Training ===")
    try:
        from core.self_training import record_interaction, get_training_stats
        
        # Record some interactions
        record_interaction("Hello JARVIS", "Hello! How can I help you today?", True)
        record_interaction("What's the weather like?", "I don't have access to weather data right now.", False)
        record_interaction("Open Chrome", "Opening Chrome.", True)
        
        # Get training stats
        stats = get_training_stats()
        print("Training stats:")
        for key, value in stats.items():
            print(f"- {key}: {value}")
        
        return True
    except Exception as e:
        print(f"Error testing self-training: {e}")
        return False

def main():
    print("JARVIS Quick Test")
    print("================")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        try:
            os.mkdir(data_dir)
            print(f"Created data directory: {data_dir}")
        except Exception as e:
            print(f"Error creating data directory: {e}")
    
    # Run tests
    tests = [
        ("Contacts", test_contacts),
        ("Calendar", test_calendar),
        ("Commands", test_commands),
        ("Self-Training", test_self_training)
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\nRunning {name} test...")
        results[name] = test_func()
    
    # Print summary
    print("\n=== Test Summary ===")
    for name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{name}: {status}")

if __name__ == "__main__":
    main()