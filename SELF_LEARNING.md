# JARVIS Self-Learning System

JARVIS includes a powerful self-learning system that allows it to automatically improve over time based on your interactions. This document explains how the self-learning system works and how you can get the most out of it.

## How Self-Learning Works

JARVIS learns from your interactions in the following ways:

1. **Interaction Recording**: Every command you give and every response JARVIS provides is recorded (locally on your computer, never sent to external servers).

2. **Success Tracking**: JARVIS tracks which interactions were successful and which ones weren't.

3. **Automatic Training Data Generation**: The system automatically converts successful interactions into training examples.

4. **Periodic Self-Training**: JARVIS periodically retrains itself using the accumulated examples.

5. **Feedback Loop**: You can provide explicit feedback on JARVIS's responses, helping it learn faster.

## Providing Feedback

After each interaction, you can provide feedback to JARVIS:

- **👍 Yes**: Indicates that JARVIS's response was helpful and correct.
- **👎 No**: Indicates that JARVIS's response was not helpful or incorrect.

Your feedback is used to improve future responses. Positive feedback reinforces good responses, while negative feedback helps JARVIS learn what not to do.

## Manual Training

You can manually trigger JARVIS's training process:

1. Click the "Train Now" button in the JARVIS interface.
2. Confirm that you want to start the training process.
3. Wait for the training to complete (this may take several minutes).

You can also run the training process from the command line:

```
python train_from_interactions.py
```

## Training Statistics

JARVIS keeps track of various training statistics:

- **Training Examples**: The number of examples JARVIS has learned from.
- **Total Interactions**: The total number of recorded interactions.
- **Successful Interactions**: The number of interactions that were successful.
- **Success Rate**: The percentage of interactions that were successful.

These statistics help you understand how well JARVIS is learning and where it might need improvement.

## How to Help JARVIS Learn Faster

To help JARVIS learn more effectively:

1. **Use Consistent Commands**: Try to use similar phrasing for the same actions.

2. **Provide Feedback**: Regularly use the feedback buttons to indicate whether responses were helpful.

3. **Correct Mistakes**: When JARVIS makes a mistake, provide the correct response if possible.

4. **Use a Variety of Commands**: Expose JARVIS to different types of commands to broaden its capabilities.

5. **Be Patient**: Learning takes time, and JARVIS will improve gradually as it collects more examples.

## Privacy and Data Storage

All interaction data is stored locally on your computer in the following files:

- `data/interactions.jsonl`: Records of all interactions
- `jarvis_model/training_data.jsonl`: Training examples generated from interactions

You can delete these files at any time to clear JARVIS's memory, though this will reset its learning progress.

## Advanced: Customizing the Learning Process

Advanced users can customize the learning process by editing the following files:

- `core/self_training.py`: Controls how interactions are recorded and how training is triggered
- `jarvis_model/Modelfile`: Defines the base model and system prompt

## Troubleshooting

If you encounter issues with the self-learning system:

- **Training Fails**: Make sure Ollama is installed and running
- **No Improvement After Training**: Try providing more explicit feedback on interactions
- **Slow Learning**: Increase the variety of commands you use with JARVIS
- **High Resource Usage**: Consider using a smaller base model in the Modelfile

## Conclusion

The self-learning system makes JARVIS more personalized and effective over time. By interacting with JARVIS regularly and providing feedback, you help it become a better assistant tailored to your specific needs and preferences.