"""
Script to manually trigger JARVIS self-training from recorded interactions.
"""

import sys
from core.self_training import generate_training_data, train_model, get_training_stats

def main():
    print("=== JARVIS Self-Training ===")
    
    # Get current training stats
    print("Current training statistics:")
    stats = get_training_stats()
    print(f"- Training examples: {stats['training_examples']}")
    print(f"- Total interactions: {stats['total_interactions']}")
    print(f"- Successful interactions: {stats['successful_interactions']}")
    print(f"- Success rate: {stats['success_rate']:.2f}%")
    print()
    
    # Generate training data
    print("Generating training data from interactions...")
    if generate_training_data():
        print("Training data generated successfully.")
    else:
        print("No new training data to generate.")
        print("You can continue using JARVIS to record more interactions.")
        return
    
    # Ask for confirmation before training
    confirm = input("Do you want to train the model now? (y/n): ")
    if confirm.lower() != 'y':
        print("Training cancelled.")
        return
    
    # Train the model
    print("Training JARVIS model...")
    if train_model():
        print("JARVIS model trained successfully!")
        print("You can now use the improved model with JARVIS.")
    else:
        print("Failed to train JARVIS model.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()