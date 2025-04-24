import os
import platform
import subprocess
import sys
import webbrowser

def install_python_dependencies():
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Python dependencies installed successfully.")

def check_ollama_installed():
    system = platform.system()
    
    if system == "Windows":
        # Check if Ollama is in PATH
        try:
            subprocess.run(["ollama", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False
    elif system == "Darwin" or system == "Linux":  # macOS or Linux
        try:
            subprocess.run(["ollama", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False
    else:
        print(f"Unsupported operating system: {system}")
        return False

def install_ollama():
    system = platform.system()
    
    if system == "Windows":
        print("Please download and install Ollama from: https://ollama.com/download/windows")
        webbrowser.open("https://ollama.com/download/windows")
        input("Press Enter after you have installed Ollama...")
    elif system == "Darwin":  # macOS
        print("Please download and install Ollama from: https://ollama.com/download/mac")
        webbrowser.open("https://ollama.com/download/mac")
        input("Press Enter after you have installed Ollama...")
    elif system == "Linux":
        print("Installing Ollama on Linux...")
        subprocess.run(["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"], shell=True)
        print("Ollama installed successfully.")
    else:
        print(f"Unsupported operating system: {system}")

def start_ollama_server():
    system = platform.system()
    
    if system == "Windows":
        print("Please start the Ollama application manually.")
        input("Press Enter after you have started Ollama...")
    elif system == "Darwin" or system == "Linux":  # macOS or Linux
        print("Starting Ollama server...")
        # Start Ollama server in the background
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Ollama server started.")

def pull_model(model_name="llama3"):
    print(f"Pulling model {model_name}...")
    subprocess.run(["ollama", "pull", model_name])
    print(f"Model {model_name} pulled successfully.")

def main():
    print("Setting up Ollama for JARVIS...")
    
    # Install Python dependencies
    install_python_dependencies()
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("Ollama is not installed.")
        install_ollama()
    
    # Start Ollama server
    start_ollama_server()
    
    # Pull the default model
    pull_model()
    
    print("\nSetup complete! You can now run JARVIS with the local LLM.")
    print("To start JARVIS, run: python main.py")

if __name__ == "__main__":
    main()