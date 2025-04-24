from voice.listen import listen
from voice.enhanced_speak import speak, set_visualization_callback
from core.local_brain import ask_local_llm as ask_gpt
from core.commands import run_command
from ui.jarvis_gui import EdithGUI
import threading
import time
import os
import sys

# Initialize enhanced self-training module
print("Initializing E.D.I.T.H. self-learning system...")
try:
    from core.self_training import initialize, get_training_stats, train_model
    
    # Get training stats
    stats = get_training_stats()
    print(f"Training stats: {stats['training_examples']} examples, {stats['total_interactions']} interactions, {stats['success_rate']:.1f}% success rate")
    
    # Check if we need to run initial training
    if stats['training_examples'] > 0 and stats['success_rate'] < 85:
        print("Optimizing neural pathways for improved accuracy...")
        train_model()
except Exception as e:
    print(f"Error initializing self-learning system: {e}")

# Print startup message
print("Initializing E.D.I.T.H. Advanced Interface...")
print("Loading visual enhancements and neural processing modules...")

# Initialize GUI with enhanced features
gui = EdithGUI()

# Set visualization callback for voice
set_visualization_callback(lambda text: gui.animate_voice_speaking(gui.generate_voice_amplitudes(text)))

# Display startup message
print("E.D.I.T.H. interface ready. Starting main loop...")

# Start the GUI main loop
gui.run()
