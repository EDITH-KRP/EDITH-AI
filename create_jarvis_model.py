import os
import subprocess
import sys
import time

def check_ollama_installed():
    try:
        import ollama
        return True
    except ImportError:
        return False

def check_ollama_server_running():
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version")
        return response.status_code == 200
    except:
        return False

def create_jarvis_model():
    print("Creating JARVIS model...")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("Ollama Python library not installed. Please install it first.")
        return False
    
    # Check if Ollama server is running
    if not check_ollama_server_running():
        print("Ollama server is not running. Please start it first.")
        return False
    
    try:
        # Import Ollama
        import ollama
        
        # Check if the base model exists
        try:
            models = ollama.list()
            base_model_exists = any(model['name'] == 'llama3' for model in models.get('models', []))
            
            if not base_model_exists:
                print("Base model 'llama3' not found. Trying to create JARVIS model without it...")
        except Exception as e:
            print(f"Error checking models: {e}")
            return False
        
        # Create the JARVIS model
        try:
            # Get the absolute path to the Modelfile
            modelfile_path = os.path.join(os.getcwd(), "jarvis_model", "Modelfile")
            
            # Create the model using the Modelfile
            print(f"Creating model from {modelfile_path}...")
            
            # Get the path to the training data
            training_data_path = os.path.join(os.getcwd(), "jarvis_model", "training_data.jsonl")
            print(f"Using training data from {training_data_path}")
            
            # Use the command-line interface to create the model
            try:
                # First try using the ollama CLI
                subprocess.run(["ollama", "create", "jarvis", "-f", modelfile_path], check=True)
                
                # After creating the base model, fine-tune it with the training data
                print("Base model created. Now fine-tuning with training data...")
                
                # Check if the training data file exists
                if os.path.exists(training_data_path):
                    try:
                        # Use Ollama's fine-tuning capability if available
                        subprocess.run([
                            "ollama", "create", "jarvis", 
                            "--from", "jarvis",
                            "--file", training_data_path
                        ], check=True)
                        print("Model fine-tuning completed successfully!")
                    except (subprocess.SubprocessError, FileNotFoundError) as e:
                        print(f"Warning: Could not fine-tune model using CLI: {e}")
                        print("The base model has been created, but without fine-tuning.")
                else:
                    print(f"Warning: Training data file not found at {training_data_path}")
                    print("The base model has been created, but without fine-tuning.")
                
            except (subprocess.SubprocessError, FileNotFoundError):
                # If that fails, try using the Python API
                with open(modelfile_path, 'r') as f:
                    modelfile = f.read()
                
                # Try different API methods
                try:
                    # Method 1
                    ollama.create(model="jarvis", modelfile=modelfile)
                    
                    # Try to fine-tune if training data exists
                    if os.path.exists(training_data_path):
                        print("Base model created. Now fine-tuning with training data...")
                        try:
                            # This is a simplified approach - actual fine-tuning may require more steps
                            import json
                            training_examples = []
                            with open(training_data_path, 'r') as f:
                                for line in f:
                                    if line.strip():
                                        training_examples.append(json.loads(line))
                            
                            # Group examples into conversations
                            conversations = []
                            current_convo = []
                            for example in training_examples:
                                current_convo.append(example)
                                if example["role"] == "assistant":
                                    conversations.append(current_convo.copy())
                                    current_convo = []
                            
                            # Train on each conversation
                            for convo in conversations:
                                messages = [{"role": msg["role"], "content": msg["content"]} for msg in convo]
                                ollama.chat(model="jarvis", messages=messages)
                                
                            print("Model fine-tuning completed!")
                        except Exception as e:
                            print(f"Warning: Could not fine-tune model using Python API: {e}")
                            print("The base model has been created, but without fine-tuning.")
                    
                except:
                    try:
                        # Method 2
                        ollama.create("jarvis", modelfile=modelfile)
                    except:
                        # Method 3 - last resort
                        import requests
                        with open(modelfile_path, 'r') as f:
                            modelfile_content = f.read()
                        
                        response = requests.post(
                            "http://localhost:11434/api/create",
                            json={"name": "jarvis", "modelfile": modelfile_content}
                        )
                        
                        if response.status_code != 200:
                            raise Exception(f"API error: {response.text}")
            
            print("JARVIS model created successfully!")
            return True
        except Exception as e:
            print(f"Error creating model: {e}")
            return False
    except Exception as e:
        print(f"Error with Ollama: {e}")
        return False

def main():
    print("=== Creating JARVIS Model ===")
    
    success = create_jarvis_model()
    
    if success:
        print("\nJARVIS model created successfully!")
        print("You can now use it by setting model_name='jarvis' in ask_local_llm function.")
    else:
        print("\nFailed to create JARVIS model.")
        print("You can still use JARVIS with fallback responses.")

if __name__ == "__main__":
    main()