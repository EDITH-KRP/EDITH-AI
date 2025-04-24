import random
import subprocess
import sys
import os
import time

# Fallback responses for when LLM is unavailable
FALLBACK_RESPONSES = {
    "hello": ["Hello! How can I help you today?", "Hi there! What can I do for you?", "Greetings! How may I assist you?"],
    "how are you": ["I'm functioning well, thank you for asking!", "I'm doing great! How about you?", "All systems operational!"],
    "what can you do": ["I can help you with various tasks like opening applications, searching the web, answering questions, and more. Just ask!", 
                       "I'm your personal assistant. I can open apps, search for information, tell you the time, and much more.",
                       "I can assist with opening programs, finding information, and answering questions. What would you like help with?"],
    "time": ["I'm sorry, I can't check the time right now.", "The time function is currently unavailable.", "I don't have access to the current time."],
    "weather": ["I'm sorry, I can't check the weather right now.", "Weather information is currently unavailable.", "I don't have access to weather data at the moment."],
    "thank you": ["You're welcome!", "Happy to help!", "Anytime!"],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Bye! Call me when you need assistance."]
}

# Check if Ollama is installed
def is_ollama_installed():
    try:
        # Try to import ollama
        import ollama
        return True
    except ImportError:
        return False

# Install Ollama if not already installed
def install_ollama():
    print("Installing Ollama Python library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    print("Ollama Python library installed successfully.")

# Check if Ollama server is running
def is_ollama_server_running():
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version")
        return response.status_code == 200
    except:
        return False

# Function to get a response from the local LLM
def get_smart_fallback(query):
    """Generate a more intelligent fallback response based on the query content"""
    query_lower = query.lower()
    
    # Check for specific question types
    if any(word in query_lower for word in ["what is", "who is", "when", "where", "why", "how"]):
        return "I don't have enough information to answer that question right now. I can help you search for it online though. Would you like me to do that?"
    
    # Check for requests for information
    if any(word in query_lower for word in ["tell me about", "explain", "describe", "information on"]):
        topic = query_lower.split("about")[-1].strip() if "about" in query_lower else query_lower.split("me")[-1].strip()
        return f"I don't have detailed information about {topic} at the moment. Would you like me to search the web for you?"
    
    # Check for requests for help
    if any(word in query_lower for word in ["help", "assist", "support"]):
        return "I can help you with opening applications, searching the web, and performing basic system tasks. What would you like me to do?"
    
    # Default response
    return "I'm here to help with tasks like opening apps, searching the web, and controlling your computer. What would you like me to do?"

def ask_local_llm(query, model_name="jarvis"):
    # First check if we have a fallback response for this query
    query_lower = query.lower()
    
    # Check if any key in FALLBACK_RESPONSES is in the query
    for key, responses in FALLBACK_RESPONSES.items():
        if key in query_lower:
            response = random.choice(responses)
            # Record this interaction
            try:
                from core.self_training import record_interaction
                record_interaction(query, response, was_successful=True)
            except Exception as e:
                print(f"Error recording interaction: {e}")
            return response
    
    # If no fallback response matches, try the local LLM
    try:
        # Check if Ollama is installed
        if not is_ollama_installed():
            print("Ollama Python library not installed. Using fallback responses.")
            response = get_smart_fallback(query)
            # Record this interaction
            try:
                from core.self_training import record_interaction
                record_interaction(query, response, was_successful=False)
            except Exception as e:
                print(f"Error recording interaction: {e}")
            return response
            
        # Import Ollama
        import ollama
        
        # Check if Ollama server is running
        if not is_ollama_server_running():
            print("Ollama server is not running. Using fallback responses.")
            response = get_smart_fallback(query)
            # Record this interaction
            try:
                from core.self_training import record_interaction
                record_interaction(query, response, was_successful=False)
            except Exception as e:
                print(f"Error recording interaction: {e}")
            return response
        
        # Try to get a response from the local LLM
        try:
            # Check if any models are available
            try:
                models = ollama.list()
                available_models = models.get('models', [])
                
                if not available_models:
                    print("No models available. Using fallback responses.")
                    response = get_smart_fallback(query)
                    # Record this interaction
                    try:
                        from core.self_training import record_interaction
                        record_interaction(query, response, was_successful=False)
                    except Exception as e:
                        print(f"Error recording interaction: {e}")
                    return response
                
                # If the specified model doesn't exist but others do, use the first available model
                model_exists = any(model['name'] == model_name for model in available_models)
                if not model_exists and available_models:
                    model_name = available_models[0]['name']
                    print(f"Using available model: {model_name}")
            except Exception as model_error:
                print(f"Error checking models: {model_error}. Using fallback responses.")
                response = get_smart_fallback(query)
                # Record this interaction
                try:
                    from core.self_training import record_interaction
                    record_interaction(query, response, was_successful=False)
                except Exception as e:
                    print(f"Error recording interaction: {e}")
                return response
            
            # Generate a response
            try:
                response = ollama.chat(
                    model=model_name,
                    messages=[{'role': 'user', 'content': query}]
                )
                
                # Extract the response text
                reply = response['message']['content'].strip()
                
                # Record this successful interaction
                try:
                    from core.self_training import record_interaction
                    record_interaction(query, reply, was_successful=True)
                except Exception as e:
                    print(f"Error recording interaction: {e}")
                
                return reply
            except Exception as chat_error:
                print(f"Error in chat: {chat_error}")
                response = get_smart_fallback(query)
                # Record this interaction
                try:
                    from core.self_training import record_interaction
                    record_interaction(query, response, was_successful=False)
                except Exception as e:
                    print(f"Error recording interaction: {e}")
                return response
        except Exception as e:
            print(f"Error using Ollama: {e}")
            response = get_smart_fallback(query)
            # Record this interaction
            try:
                from core.self_training import record_interaction
                record_interaction(query, response, was_successful=False)
            except Exception as e:
                print(f"Error recording interaction: {e}")
            return response
    except Exception as e:
        print(f"Error with local LLM: {e}")
        response = get_smart_fallback(query)
        # Record this interaction
        try:
            from core.self_training import record_interaction
            record_interaction(query, response, was_successful=False)
        except Exception as e:
            print(f"Error recording interaction: {e}")
        return response

# For backward compatibility
def ask_gpt(query):
    return ask_local_llm(query)