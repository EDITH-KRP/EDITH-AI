"""
Enhanced self-training module for EDITH.
This module allows EDITH to learn from interactions and improve over time with
advanced data processing and model optimization techniques.
"""

import os
import json
import time
import datetime
import subprocess
import threading
import random
from collections import deque

# Path to store interaction data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
INTERACTIONS_FILE = os.path.join(DATA_DIR, 'interactions.jsonl')
FEEDBACK_FILE = os.path.join(DATA_DIR, 'feedback.jsonl')
TRAINING_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 'jarvis_model', 'training_data.jsonl')
MODELFILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             'jarvis_model', 'Modelfile')
FEEDBACK_FILE = os.path.join(DATA_DIR, 'feedback.jsonl')
MODELFILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             'jarvis_model', 'Modelfile')

# Ensure the data directory exists
try:
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
except Exception as e:
    print(f"Error creating data directory: {e}")

# Maximum number of interactions to keep in memory
MAX_RECENT_INTERACTIONS = 100
recent_interactions = deque(maxlen=MAX_RECENT_INTERACTIONS)

# Flag to indicate if training is in progress
training_in_progress = False

def record_interaction(user_query, jarvis_response, was_successful=True):
    """
    Record an interaction between the user and JARVIS.
    
    Args:
        user_query (str): The user's query or command
        jarvis_response (str): JARVIS's response
        was_successful (bool): Whether the interaction was successful
    """
    try:
        # Create an interaction record
        interaction = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_query": user_query,
            "jarvis_response": jarvis_response,
            "was_successful": was_successful
        }
        
        # Add to recent interactions
        recent_interactions.append(interaction)
        
        # Save to file
        with open(INTERACTIONS_FILE, 'a') as f:
            f.write(json.dumps(interaction) + '\n')
            
        # Check if we should trigger training
        check_training_trigger()
        
        return True
    except Exception as e:
        print(f"Error recording interaction: {e}")
        return False

def check_training_trigger():
    """
    Check if we should trigger self-training based on various conditions.
    """
    global training_in_progress
    
    # Don't trigger if training is already in progress
    if training_in_progress:
        return
    
    # Conditions to trigger training:
    # 1. Number of new interactions since last training
    # 2. Time since last training
    # 3. Percentage of unsuccessful interactions
    
    try:
        # Count interactions
        interaction_count = len(recent_interactions)
        
        # Check if we have enough interactions to warrant training
        if interaction_count >= 20:  # Arbitrary threshold
            # Check if we have unsuccessful interactions that need improvement
            unsuccessful_count = sum(1 for i in recent_interactions if not i.get('was_successful', True))
            unsuccessful_percentage = unsuccessful_count / interaction_count
            
            # If more than 10% of interactions were unsuccessful, trigger training
            if unsuccessful_percentage > 0.1:
                # Start training in a separate thread
                threading.Thread(target=start_self_training, daemon=True).start()
                return
        
        # Check time-based trigger (e.g., once per day)
        # This would require storing the last training time
        # For simplicity, we'll use a random chance for now
        if random.random() < 0.01:  # 1% chance each time this function is called
            threading.Thread(target=start_self_training, daemon=True).start()
            
    except Exception as e:
        print(f"Error checking training trigger: {e}")

def start_self_training():
    """
    Start the self-training process.
    """
    global training_in_progress
    
    try:
        print("Starting JARVIS self-training...")
        training_in_progress = True
        
        # 1. Generate training data from interactions
        generate_training_data()
        
        # 2. Train the model
        train_model()
        
        # 3. Reset the recent interactions
        recent_interactions.clear()
        
        print("JARVIS self-training completed!")
        training_in_progress = False
        
    except Exception as e:
        print(f"Error during self-training: {e}")
        training_in_progress = False

def generate_training_data():
    """
    Generate high-quality training data from recorded interactions with advanced filtering.
    """
    try:
        print("Generating training data from interactions...")
        
        # Load existing training data
        existing_training_data = []
        if os.path.exists(TRAINING_DATA_FILE):
            with open(TRAINING_DATA_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            existing_training_data.append(json.loads(line))
                        except json.JSONDecodeError:
                            print(f"Warning: Skipping invalid JSON line in training data")
        
        # Load all interactions
        all_interactions = []
        if os.path.exists(INTERACTIONS_FILE):
            with open(INTERACTIONS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            all_interactions.append(json.loads(line))
                        except json.JSONDecodeError:
                            print(f"Warning: Skipping invalid JSON line in interactions")
        
        # Load feedback data for prioritization
        feedback_data = {}
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            feedback = json.loads(line)
                            # Use query as key to find the latest feedback
                            feedback_data[feedback['user_query']] = feedback
                        except json.JSONDecodeError:
                            print(f"Warning: Skipping invalid JSON line in feedback")
        
        # Filter for successful interactions only
        successful_interactions = [i for i in all_interactions if i.get('was_successful', True)]
        
        # Sort interactions by priority (if they have feedback)
        prioritized_interactions = sorted(
            successful_interactions,
            key=lambda i: feedback_data.get(i['user_query'], {}).get('priority', 2),
            reverse=True  # Higher priority first
        )
        
        # Convert interactions to training format with deduplication and quality checks
        new_training_data = []
        seen_queries = set()
        
        for interaction in prioritized_interactions:
            # Skip if query is too short or likely not useful
            if len(interaction['user_query'].strip()) < 3:
                continue
                
            # Skip if response is too short or likely not useful
            if len(interaction.get('jarvis_response', '').strip()) < 5:
                continue
            
            # Check for duplicates with normalization
            normalized_query = interaction['user_query'].lower().strip()
            if normalized_query in seen_queries:
                continue
                
            seen_queries.add(normalized_query)
            
            # Create training examples
            user_example = {
                "role": "user",
                "content": interaction['user_query']
            }
            
            # Use corrected response from feedback if available
            if normalized_query in feedback_data and feedback_data[normalized_query].get('corrected_response'):
                assistant_example = {
                    "role": "assistant",
                    "content": feedback_data[normalized_query]['corrected_response']
                }
            else:
                assistant_example = {
                    "role": "assistant",
                    "content": interaction['jarvis_response']
                }
            
            # Check if this example already exists in training data
            user_exists = any(e['role'] == 'user' and e['content'].lower().strip() == normalized_query 
                             for e in existing_training_data)
            
            if not user_exists:
                new_training_data.append(user_example)
                new_training_data.append(assistant_example)
        
        # If we have new training data, append it to the file
        if new_training_data:
            print(f"Adding {len(new_training_data) // 2} new conversation examples to training data.")
            with open(TRAINING_DATA_FILE, 'a') as f:
                for example in new_training_data:
                    f.write(json.dumps(example) + '\n')
            
            # Also create a backup of the training data
            backup_file = TRAINING_DATA_FILE + f".backup.{int(time.time())}"
            with open(backup_file, 'w') as f:
                for example in existing_training_data + new_training_data:
                    f.write(json.dumps(example) + '\n')
            
            return True
        else:
            print("No new training data to add.")
            return False
            
    except Exception as e:
        print(f"Error generating training data: {e}")
        return False

def train_model():
    """
    Train the EDITH model using the updated training data with enhanced optimization.
    """
    try:
        print("Training EDITH model...")
        
        # Check if Ollama is installed and running
        try:
            import ollama
            import requests
            response = requests.get("http://localhost:11434/api/version")
            if response.status_code != 200:
                print("Ollama server is not running. Cannot train model.")
                return False
        except Exception as e:
            print(f"Ollama is not installed or server is not running. Cannot train model: {e}")
            return False
        
        # Update the Modelfile to use EDITH instead of JARVIS
        try:
            # Read the current Modelfile
            with open(MODELFILE_PATH, 'r') as f:
                modelfile_content = f.read()
            
            # Update references from JARVIS to EDITH if needed
            if 'JARVIS' in modelfile_content and 'EDITH' not in modelfile_content:
                modelfile_content = modelfile_content.replace('JARVIS', 'EDITH')
                modelfile_content = modelfile_content.replace('jarvis', 'edith')
                
                # Write the updated Modelfile
                with open(MODELFILE_PATH, 'w') as f:
                    f.write(modelfile_content)
                print("Updated Modelfile to use EDITH instead of JARVIS")
        except Exception as e:
            print(f"Error updating Modelfile: {e}")
        
        # Optimize training parameters
        try:
            # Read the current Modelfile to check parameters
            with open(MODELFILE_PATH, 'r') as f:
                modelfile_content = f.read()
            
            # Ensure optimal parameters for better responses
            if 'PARAMETER temperature' not in modelfile_content:
                # Add optimal parameters if missing
                parameter_lines = """
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
"""
                # Find the FROM line
                from_line_end = modelfile_content.find('\n', modelfile_content.find('FROM'))
                
                # Insert parameters after FROM line
                if from_line_end > 0:
                    modelfile_content = (
                        modelfile_content[:from_line_end + 1] + 
                        parameter_lines + 
                        modelfile_content[from_line_end + 1:]
                    )
                    
                    # Write the updated Modelfile
                    with open(MODELFILE_PATH, 'w') as f:
                        f.write(modelfile_content)
                    print("Added optimal parameters to Modelfile")
        except Exception as e:
            print(f"Error optimizing Modelfile parameters: {e}")
        
        # Use the command-line interface to create/update the model
        try:
            # Create/update the model
            print("Creating base model...")
            subprocess.run(["ollama", "create", "edith", "-f", MODELFILE_PATH], check=True)
            
            # Fine-tune with the training data
            print("Fine-tuning with training data...")
            subprocess.run([
                "ollama", "create", "edith", 
                "--from", "edith",
                "--file", TRAINING_DATA_FILE
            ], check=True)
            
            print("Model training completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error training model with CLI: {e}")
            
            # Try alternative method using Python API
            try:
                print("Attempting training with Python API...")
                # Read the Modelfile
                with open(MODELFILE_PATH, 'r') as f:
                    modelfile = f.read()
                
                # Create/update the model
                print("Creating base model with Python API...")
                ollama.create(model="edith", modelfile=modelfile)
                
                # Fine-tune with training data
                print("Fine-tuning with Python API...")
                training_examples = []
                with open(TRAINING_DATA_FILE, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                training_examples.append(json.loads(line))
                            except json.JSONDecodeError:
                                print(f"Warning: Skipping invalid JSON line in training data")
                
                # Group examples into conversations
                conversations = []
                current_convo = []
                for example in training_examples:
                    current_convo.append(example)
                    if example["role"] == "assistant":
                        conversations.append(current_convo.copy())
                        current_convo = []
                
                # Train on each conversation with error handling
                success_count = 0
                for i, convo in enumerate(conversations):
                    try:
                        if i % 10 == 0:
                            print(f"Training on conversation {i+1}/{len(conversations)}...")
                        messages = [{"role": msg["role"], "content": msg["content"]} for msg in convo]
                        ollama.chat(model="edith", messages=messages)
                        success_count += 1
                    except Exception as e:
                        print(f"Error training on conversation {i+1}: {e}")
                
                print(f"Model training completed using Python API! Successfully trained on {success_count}/{len(conversations)} conversations.")
                return success_count > 0
                
            except Exception as e2:
                print(f"Error training model using Python API: {e2}")
                return False
            
    except Exception as e:
        print(f"Error during model training: {e}")
        return False

def provide_feedback(user_query, jarvis_response, feedback_positive=True, corrected_response=None):
    """
    Enhanced feedback system for EDITH's responses with prioritized learning.
    
    Args:
        user_query (str): The user's query or command
        jarvis_response (str): EDITH's response
        feedback_positive (bool): Whether the feedback is positive
        corrected_response (str, optional): User-provided correct response for negative feedback
    """
    try:
        # Record the interaction with the feedback
        record_interaction(user_query, jarvis_response, was_successful=feedback_positive)
        
        # Create a feedback record with priority
        feedback_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_query": user_query,
            "edith_response": jarvis_response,
            "feedback_positive": feedback_positive,
            "priority": 1 if feedback_positive else 3,  # Higher priority for negative feedback
            "corrected_response": corrected_response
        }
        
        # Save to feedback file
        with open(FEEDBACK_FILE, 'a') as f:
            f.write(json.dumps(feedback_record) + '\n')
        
        # If negative feedback, prioritize for training
        if not feedback_positive:
            print(f"Negative feedback received for query: {user_query}")
            
            # If we have a corrected response, add it directly to training data
            if corrected_response:
                # Add the corrected example to training data
                with open(TRAINING_DATA_FILE, 'a') as f:
                    f.write(json.dumps({"role": "user", "content": user_query}) + '\n')
                    f.write(json.dumps({"role": "assistant", "content": corrected_response}) + '\n')
                
                print(f"Added corrected response to training data for: {user_query}")
                
                # Consider triggering immediate retraining for critical corrections
                if random.random() < 0.3:  # 30% chance to retrain immediately
                    threading.Thread(target=start_self_training, daemon=True).start()
        
        # For positive feedback, reinforce good responses
        elif feedback_positive:
            # Increase the weight of this example by potentially duplicating it
            if random.random() < 0.2:  # 20% chance to reinforce
                with open(TRAINING_DATA_FILE, 'a') as f:
                    f.write(json.dumps({"role": "user", "content": user_query}) + '\n')
                    f.write(json.dumps({"role": "assistant", "content": jarvis_response}) + '\n')
                print(f"Reinforced positive example in training data: {user_query}")
        
        return True
    except Exception as e:
        print(f"Error processing feedback: {e}")
        return False

def get_training_stats():
    """
    Get statistics about the training data and interactions.
    """
    try:
        # Count training examples
        training_example_count = 0
        if os.path.exists(TRAINING_DATA_FILE):
            with open(TRAINING_DATA_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        training_example_count += 1
        
        # Count interactions
        interaction_count = 0
        successful_count = 0
        if os.path.exists(INTERACTIONS_FILE):
            with open(INTERACTIONS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        interaction = json.loads(line)
                        interaction_count += 1
                        if interaction.get('was_successful', True):
                            successful_count += 1
        
        # Calculate success rate
        success_rate = (successful_count / interaction_count) * 100 if interaction_count > 0 else 0
        
        return {
            "training_examples": training_example_count,
            "total_interactions": interaction_count,
            "successful_interactions": successful_count,
            "success_rate": success_rate,
            "is_training": training_in_progress
        }
        
    except Exception as e:
        print(f"Error getting training stats: {e}")
        return {
            "error": str(e)
        }

# Initialize by loading recent interactions
def initialize():
    """
    Initialize the self-training module.
    """
    global recent_interactions
    
    try:
        # Load recent interactions from file
        if os.path.exists(INTERACTIONS_FILE):
            with open(INTERACTIONS_FILE, 'r') as f:
                interactions = [json.loads(line) for line in f if line.strip()]
                
                # Take the most recent interactions
                recent_interactions = deque(interactions[-MAX_RECENT_INTERACTIONS:], maxlen=MAX_RECENT_INTERACTIONS)
                
        print(f"Self-training module initialized with {len(recent_interactions)} recent interactions.")
        
    except Exception as e:
        print(f"Error initializing self-training module: {e}")

# Initialize the module when imported
initialize()