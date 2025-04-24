import os
import json
import re

# Path to the contacts file
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CONTACTS_FILE = os.path.join(DATA_DIR, 'contacts.json')

# Ensure the data directory exists
try:
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
except Exception as e:
    print(f"Error creating data directory: {e}")

def load_contacts():
    """Load contacts from the JSON file"""
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, return an empty contacts list
            return []
    else:
        # If the file doesn't exist, create it with an empty list
        save_contacts([])
        return []

def save_contacts(contacts):
    """Save contacts to the JSON file"""
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=4)

def add_contact(name, phone=None, email=None, whatsapp=None):
    """Add a new contact or update an existing one"""
    contacts = load_contacts()
    
    # Check if contact already exists
    for i, contact in enumerate(contacts):
        if contact['name'].lower() == name.lower():
            # Update existing contact
            if phone:
                contacts[i]['phone'] = phone
            if email:
                contacts[i]['email'] = email
            if whatsapp:
                contacts[i]['whatsapp'] = whatsapp
            save_contacts(contacts)
            return f"Updated contact: {name}"
    
    # Add new contact
    new_contact = {'name': name}
    if phone:
        new_contact['phone'] = phone
    if email:
        new_contact['email'] = email
    if whatsapp:
        new_contact['whatsapp'] = whatsapp
    
    contacts.append(new_contact)
    save_contacts(contacts)
    return f"Added new contact: {name}"

def find_contact(name):
    """Find a contact by name"""
    contacts = load_contacts()
    
    # Try exact match first
    for contact in contacts:
        if contact['name'].lower() == name.lower():
            return contact
    
    # Try partial match
    for contact in contacts:
        if name.lower() in contact['name'].lower():
            return contact
    
    return None

def delete_contact(name):
    """Delete a contact by name"""
    contacts = load_contacts()
    initial_count = len(contacts)
    
    # Remove contacts with matching name
    contacts = [c for c in contacts if c['name'].lower() != name.lower()]
    
    if len(contacts) < initial_count:
        save_contacts(contacts)
        return f"Deleted contact: {name}"
    else:
        return f"Contact not found: {name}"

def list_contacts():
    """Return a formatted list of all contacts"""
    contacts = load_contacts()
    
    if not contacts:
        return "No contacts found."
    
    result = "Your contacts:\n"
    for contact in contacts:
        result += f"- {contact['name']}"
        if 'phone' in contact:
            result += f" (Phone: {contact['phone']})"
        if 'email' in contact:
            result += f" (Email: {contact['email']})"
        result += "\n"
    
    return result

def parse_contact_command(command):
    """Parse a natural language command to manage contacts"""
    command = command.lower()
    
    # Add contact
    add_match = re.search(r"add contact (?:named |called )?([a-zA-Z\s]+)(?: with)?(?: phone ([0-9\s\-\+]+))?(?: email ([a-zA-Z0-9@\.\-_]+))?(?: whatsapp ([0-9\s\-\+]+))?", command)
    if add_match:
        name = add_match.group(1).strip()
        phone = add_match.group(2).strip() if add_match.group(2) else None
        email = add_match.group(3).strip() if add_match.group(3) else None
        whatsapp = add_match.group(4).strip() if add_match.group(4) else phone  # Use phone as whatsapp if not specified
        
        return add_contact(name, phone, email, whatsapp)
    
    # Find contact
    find_match = re.search(r"find contact (?:named |called )?([a-zA-Z\s]+)", command)
    if find_match:
        name = find_match.group(1).strip()
        contact = find_contact(name)
        
        if contact:
            result = f"Contact: {contact['name']}\n"
            if 'phone' in contact:
                result += f"Phone: {contact['phone']}\n"
            if 'email' in contact:
                result += f"Email: {contact['email']}\n"
            if 'whatsapp' in contact:
                result += f"WhatsApp: {contact['whatsapp']}\n"
            return result
        else:
            return f"Contact not found: {name}"
    
    # Delete contact
    delete_match = re.search(r"delete contact (?:named |called )?([a-zA-Z\s]+)", command)
    if delete_match:
        name = delete_match.group(1).strip()
        return delete_contact(name)
    
    # List contacts
    if "list contacts" in command or "show contacts" in command or "show my contacts" in command:
        return list_contacts()
    
    return None