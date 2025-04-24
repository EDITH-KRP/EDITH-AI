# JARVIS - Your Personal AI Assistant

JARVIS is a powerful voice-controlled AI assistant that can control your entire laptop, from opening applications to playing specific music and interacting with various programs.

## Features

### Application Control
- Open any installed application on your system
- Close applications and windows
- Minimize, maximize, and restore windows
- Switch between windows and applications
- Perform app-specific actions and searches

### Messaging & Communication
- Send WhatsApp messages to contacts
- Send SMS messages
- Compose emails
- Make voice and video calls
- Manage contacts (add, find, delete, list)

### Calendar & Reminders
- Add events to your calendar
- View upcoming events
- Check schedule for specific dates
- Delete or modify events

### Music Control
- Play specific songs by name and artist
- Control music playback (play, pause, next, previous)
- Adjust volume
- Search for music on Spotify or YouTube Music

### Web Browsing
- Open websites
- Search the web (Google, YouTube)
- Control browser tabs (new tab, close tab, switch tabs)
- Navigate to specific URLs
- Refresh pages
- Search within specific websites and services

### Document Editing
- Create new documents in Microsoft Office applications
- Save documents
- Format text (bold, italic, underline)
- Copy, cut, and paste content
- Select all content
- Undo and redo actions

### System Control
- Shutdown, restart, or sleep your computer
- Take screenshots
- Get system information
- List installed applications

### Text Input and Keyboard Control
- Type text in any application
- Press special keys (Enter, Tab, Escape, arrows)
- Send keyboard shortcuts

### File Management
- Create folders
- Delete files
- List files in directories

### Voice Interaction
- Voice recognition and text-to-speech capabilities
- Natural language understanding
- Contextual responses using local LLM (when available)

## Requirements

- Python 3.8 or higher
- Ollama (for running the local LLM)
- A microphone for voice input
- Speakers for voice output

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/jarvis.git
   cd jarvis
   ```

2. Run the setup script to install dependencies and set up Ollama:
   ```
   python setup_ollama.py
   ```

   This script will:
   - Install Python dependencies
   - Help you install Ollama if it's not already installed
   - Start the Ollama server
   - Download the default language model (llama3)

## Usage

1. Start JARVIS:
   ```
   python main.py
   ```

2. Speak to JARVIS using natural language commands:

### Opening Applications
- "Open Chrome"
- "Open Microsoft Word"
- "Open Spotify"
- "Open Calculator"
- "Open File Explorer"

### Messaging & Communication
- "Send message to John on WhatsApp saying I'll be late"
- "Send SMS to Mom saying I'll call later"
- "Send email to boss@example.com subject Meeting report body Here's the report"
- "Call Sarah on WhatsApp"
- "Video call Mike on Teams"
- "Add contact named John Smith with phone 555-1234 email john@example.com"
- "Find contact named Sarah"
- "List contacts"

### Calendar & Reminders
- "Add event called Team Meeting on tomorrow at 3pm"
- "What's on today?"
- "Show my upcoming events"
- "Show events for next Monday"
- "Delete event Team Meeting on tomorrow"

### App-Specific Search
- "Search for vacation photos in Google Photos"
- "Search for budget spreadsheet in Google Drive"
- "Search for Python tutorials in YouTube"
- "Search for Taylor Swift in Spotify"
- "Open presentation in PowerPoint"
- "Create new document in Word"

### Music Control
- "Play Shape of You by Ed Sheeran"
- "Play some music"
- "Play the next song"
- "Pause the music"
- "Volume up"
- "Volume down"

### Web Browsing
- "Open YouTube"
- "Search for Python tutorials"
- "Open a new tab"
- "Close this tab"
- "Go to github.com"
- "Refresh the page"

### Window Control
- "Close this window"
- "Minimize window"
- "Maximize window"
- "Switch window"
- "What window is this?"

### Text and Keyboard Input
- "Type Hello, how are you?"
- "Press Enter"
- "Press Tab"
- "Press Escape"
- "Copy"
- "Paste"
- "Select all"
- "Undo"
- "Redo"

### System Commands
- "Shutdown computer"
- "Restart computer"
- "Sleep computer"
- "Take a screenshot"
- "List installed apps"

3. To exit JARVIS, say "Exit" or "Quit".

## Advanced Features

### Local LLM Integration
JARVIS can use a local LLM (Language Model) through Ollama to provide more intelligent responses. To enable this feature:

1. Install Ollama from https://ollama.com/download
2. Start the Ollama application
3. Pull a model: `ollama pull llama3` (or another model of your choice)
4. JARVIS will automatically use the local LLM when available

### Changing the LLM Model

By default, JARVIS uses the "jarvis" model (or falls back to "llama3"). To use a different model:

1. Pull the model using Ollama:
   ```
   ollama pull mistral
   ```

2. Edit the `core/local_brain.py` file and change the default model name in the `ask_local_llm` function:
   ```python
   def ask_local_llm(query, model_name="mistral"):
   ```

### App Automation
JARVIS can automate interactions with various applications using PyAutoGUI. This allows it to:

- Click on specific positions or images on the screen
- Send keyboard shortcuts to applications
- Interact with specific applications like browsers, Office apps, and media players

### Adding New Commands

To add new commands, edit the `core/commands.py` file and add your command to the `run_command` function.

### Customizing App Detection

JARVIS automatically detects installed applications on your system. You can customize the app detection by:

1. Adding common paths to the `get_common_program_paths` function in `core/app_finder.py`
2. Enabling full system scanning by uncommenting the line in `get_installed_apps_list` function

## Troubleshooting

### Speech Recognition Issues
- Make sure your microphone is properly connected and set as the default input device
- Speak clearly and at a moderate pace
- Try to minimize background noise

### Application Control Issues
- Some applications may require administrator privileges to be controlled
- Certain applications may have unique interfaces that JARVIS is not specifically programmed to handle
- For best results, make sure applications are in their default window state

### Local LLM Issues
- If Ollama is not installed or running, JARVIS will fall back to using predefined responses
- Make sure you have enough disk space and RAM to run the local LLM
- Larger models provide better responses but require more resources

### Testing Ollama
You can test if Ollama is working correctly by running:
```
python test_ollama.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the GPT models that helped create this project
- The developers of all the libraries used in this project
- The open-source community for their continuous support and inspiration