"""
Test script for the JARVIS model.
This script allows you to interact with the JARVIS model directly to test its responses.
"""

import ollama
import sys

def test_jarvis_model():
    print("=== JARVIS Model Test ===")
    print("Type 'exit' or 'quit' to end the test.")
    print()
    
    # Check if the model exists
    try:
        models = ollama.list()
        model_exists = any(model['name'] == 'jarvis' for model in models.get('models', []))
        
        if not model_exists:
            print("Error: JARVIS model not found.")
            print("Please run 'python create_jarvis_model.py' first.")
            return
    except Exception as e:
        print(f"Error checking models: {e}")
        return
    
    # Start conversation
    messages = []
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting JARVIS model test.")
            break
        
        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Get response from JARVIS model
            response = ollama.chat(
                model="jarvis",
                messages=messages
            )
            
            # Extract and print the response
            assistant_message = response['message']['content']
            print(f"\nJARVIS: {assistant_message}")
            
            # Add assistant message to conversation
            messages.append({"role": "assistant", "content": assistant_message})
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    # Check if Ollama is installed
    try:
        import ollama
    except ImportError:
        print("Error: Ollama Python library not installed.")
        print("Please install it with: pip install ollama")
        sys.exit(1)
    
    # Check if Ollama server is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code != 200:
            print("Error: Ollama server is not running.")
            print("Please start the Ollama server first.")
            sys.exit(1)
    except:
        print("Error: Ollama server is not running or not accessible.")
        print("Please start the Ollama server first.")
        sys.exit(1)
    
    # Run the test
    test_jarvis_model()