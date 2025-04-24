from openai import OpenAI
import random

# Initialize the client
client = OpenAI(api_key="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")  # Replace with your key

# Fallback responses for when OpenAI API is unavailable
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

def ask_gpt(query):
    # First check if we have a fallback response for this query
    query_lower = query.lower()
    
    # Check if any key in FALLBACK_RESPONSES is in the query
    for key, responses in FALLBACK_RESPONSES.items():
        if key in query_lower:
            return random.choice(responses)
    
    # If no fallback response matches, try the OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=150,
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        # Provide a more helpful response for common errors
        error_str = str(e)
        if "insufficient_quota" in error_str:
            return "I'm sorry, but the OpenAI API quota has been exceeded. I'll try to answer with my built-in knowledge instead. What would you like to know?"
        elif "model_not_found" in error_str:
            return "I'm sorry, but the requested AI model is not available. I'll use my built-in responses instead. How can I help you?"
        elif "invalid_request_error" in error_str:
            return "There was an issue with the request to the AI service. I'll try to help with my built-in knowledge. What do you need?"
        else:
            # Generic fallback response when no specific match is found
            return "I'm here to help. You can ask me to open applications, search the web, or assist with basic tasks."
