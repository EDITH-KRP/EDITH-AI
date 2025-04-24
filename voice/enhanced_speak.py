import pyttsx3
import threading
import time
import random
import numpy as np

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set properties
engine.setProperty('rate', 180)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

# Try to set a more robotic/AI-like voice
voices = engine.getProperty('voices')
for voice in voices:
    # Look for a voice that sounds more robotic or AI-like
    if 'david' in voice.id.lower() or 'mark' in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break

# Callback function for visualization
visualization_callback = None

def set_visualization_callback(callback):
    """Set the callback function for visualization"""
    global visualization_callback
    visualization_callback = callback

def speak(text, gui=None):
    """
    Enhanced speak function with visualization support
    
    Args:
        text (str): The text to speak
        gui (object, optional): GUI object with visualization methods
    """
    # Generate amplitudes for visualization
    if gui and hasattr(gui, 'generate_voice_amplitudes'):
        amplitudes = gui.generate_voice_amplitudes(text)
    else:
        amplitudes = None
    
    # Start visualization in a separate thread
    if gui and hasattr(gui, 'animate_voice_speaking'):
        viz_thread = threading.Thread(
            target=_run_visualization,
            args=(gui, text, amplitudes),
            daemon=True
        )
        viz_thread.start()
    
    # Speak the text
    engine.say(text)
    engine.runAndWait()
    
    # Return to idle visualization after speaking
    if gui and hasattr(gui, 'animate_voice_idle'):
        gui.root.after(100, gui.animate_voice_idle)

def _run_visualization(gui, text, amplitudes):
    """Run the visualization while speaking"""
    # Calculate approximate speaking time (5 chars per second)
    speak_time = len(text) / 5
    
    # Minimum time for very short texts
    speak_time = max(speak_time, 1.5)
    
    # Number of animation frames
    frames = int(speak_time * 20)  # 20 frames per second
    
    # Run visualization
    for _ in range(frames):
        if gui and hasattr(gui, 'animate_voice_speaking'):
            gui.root.after_idle(lambda: gui.animate_voice_speaking(amplitudes))
        time.sleep(0.05)  # 50ms per frame