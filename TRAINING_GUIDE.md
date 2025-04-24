# JARVIS Model Training Guide

This guide explains how to train and use the custom JARVIS model to enable all the assistant's capabilities.

## Prerequisites

Before training the JARVIS model, make sure you have:

1. Installed Ollama from [https://ollama.com/download](https://ollama.com/download)
2. Started the Ollama application
3. Installed the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Training the JARVIS Model

The JARVIS model is created by:
1. Using a base model (llama3)
2. Customizing it with a system prompt that defines JARVIS's capabilities
3. Fine-tuning it with example conversations

### Step 1: Create the Base Model

Run the following command to create the JARVIS model:

```
python create_jarvis_model.py
```

This script will:
- Check if Ollama is installed and running
- Create a new model called "jarvis" based on the Modelfile in the jarvis_model directory
- Fine-tune the model using the training examples in training_data.jsonl

The process may take several minutes depending on your computer's specifications.

### Step 2: Test the Model

After creating the model, you can test it directly:

```
python test_jarvis_model.py
```

This will start an interactive session where you can chat with the JARVIS model and test its understanding of various commands.

### Step 3: Use the Model with JARVIS

The main JARVIS application is already configured to use the custom model. Simply run:

```
python main.py
```

JARVIS will automatically use the custom model for responding to commands that aren't directly handled by the command processor.

## Customizing the Model

You can customize the JARVIS model in several ways:

### Modifying the System Prompt

The system prompt defines JARVIS's personality and capabilities. You can edit it in:
```
jarvis_model/Modelfile
```

### Adding Training Examples

To improve JARVIS's understanding of commands, you can add more examples to:
```
jarvis_model/training_data.jsonl
```

Each line should be a valid JSON object with "role" (either "user" or "assistant") and "content" fields.

### Using a Different Base Model

If you want to use a different base model, edit the first line in the Modelfile:
```
FROM llama3
```

Replace "llama3" with another model available in Ollama, such as "mistral" or "phi".

## Troubleshooting

### Model Creation Fails

If model creation fails, try:
1. Make sure Ollama is running
2. Check that you have enough disk space
3. Try pulling the base model manually:
   ```
   ollama pull llama3
   ```
4. Check the Ollama logs for errors

### Model Responses Are Incorrect

If the model doesn't respond correctly to commands:
1. Add more training examples for that specific type of command
2. Make sure the command is properly described in the system prompt
3. Recreate the model after making changes

### Performance Issues

If the model is slow to respond:
1. Consider using a smaller base model
2. Adjust the parameters in the Modelfile (temperature, top_p, top_k)
3. Make sure your computer meets the minimum requirements for running the model

## Advanced: Creating a Custom Modelfile

For advanced users, you can create a completely custom Modelfile with more specific instructions and parameters. The Ollama documentation provides details on all available options:

[https://github.com/ollama/ollama/blob/main/docs/modelfile.md](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

## Conclusion

Training a custom model for JARVIS enhances its ability to understand and respond to your commands. As you use JARVIS more, you can continue to improve the model by adding more training examples based on your specific needs and usage patterns.