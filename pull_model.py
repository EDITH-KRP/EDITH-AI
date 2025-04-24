import ollama
import sys

def main():
    model_name = "llama3"
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    
    print(f"Pulling model: {model_name}")
    print("This may take a while depending on your internet connection...")
    
    try:
        ollama.pull(model_name)
        print(f"Successfully pulled model: {model_name}")
    except Exception as e:
        print(f"Error pulling model: {e}")

if __name__ == "__main__":
    main()