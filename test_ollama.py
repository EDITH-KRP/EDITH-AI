import sys

def check_ollama_installed():
    try:
        import ollama
        print("[OK] Ollama Python library is installed.")
        return True
    except ImportError:
        print("[ERROR] Ollama Python library is not installed.")
        print("   Run: pip install ollama")
        return False

def check_ollama_server():
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code == 200:
            print(f"[OK] Ollama server is running. Version: {response.json().get('version', 'unknown')}")
            return True
        else:
            print(f"[ERROR] Ollama server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Ollama server is not running or not accessible: {e}")
        print("   Please download and install Ollama from: https://ollama.com/download")
        print("   Then start the Ollama application.")
        return False

def check_models():
    try:
        import ollama
        models = ollama.list()
        if models and 'models' in models and models['models']:
            print("[OK] Available models:")
            for model in models['models']:
                print(f"   - {model['name']}")
            return True
        else:
            print("[ERROR] No models found.")
            print("   Run: ollama pull llama3")
            return False
    except Exception as e:
        print(f"[ERROR] Could not list models: {e}")
        return False

def test_query():
    try:
        import ollama
        models = ollama.list()
        if not models or 'models' not in models or not models['models']:
            print("[ERROR] No models available to test.")
            return False
        
        model_name = models['models'][0]['name']
        print(f"Testing query with model: {model_name}")
        
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': 'Hello, how are you?'}]
        )
        
        reply = response['message']['content'].strip()
        print(f"[OK] Model response: {reply[:100]}...")
        return True
    except Exception as e:
        print(f"[ERROR] Error testing query: {e}")
        return False

def main():
    print("=== Ollama Test ===")
    
    if not check_ollama_installed():
        return
    
    if not check_ollama_server():
        return
    
    if not check_models():
        return
    
    test_query()
    
    print("\nIf all checks passed, you're ready to use JARVIS with Ollama!")
    print("Run: python main.py")

if __name__ == "__main__":
    main()