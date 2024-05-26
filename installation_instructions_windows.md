# Installation Instructions for Voice Command Listener for Minecraft on Windows

## Prerequisites
1. Ensure you have Python installed on your Windows machine. You can download Python from the official website: https://www.python.org/downloads/
2. During the installation, make sure to check the box that says "Add Python to PATH."

## Step-by-Step Installation

### Step 1: Install Python and Pip
1. Download and install Python from the official website: https://www.python.org/downloads/
2. Verify the installation by opening Command Prompt and running:
   ```
   python --version
   pip --version
   ```

### Step 2: Install PortAudio
1. Download and install PortAudio from the official website: http://www.portaudio.com/download.html
2. Alternatively, you can use a package manager like Chocolatey to install PortAudio:
   ```
   choco install portaudio
   ```

### Step 3: Install Required Python Libraries
1. Open Command Prompt and run the following commands to install the necessary libraries:
   ```
   pip install git+https://github.com/openai/whisper.git
   pip install pyaudio numpy
   ```

### Step 4: Download the Voice Command Listener Script
1. Save the `voice_command_listener.py` script to a directory of your choice.

### Step 5: Run the Script
1. Open Command Prompt and navigate to the directory where you saved the `voice_command_listener.py` script.
2. Run the script using the following command:
   ```
   python voice_command_listener.py --trigger "execute command" --command "/give @p diamond 1" --duration 30
   ```

### Step 6: (Optional) Enable the GUI
1. If you want to use the GUI, open the `voice_command_listener.py` script in a text editor.
2. Uncomment the line that says `# create_gui()` at the end of the script.
3. Save the changes and run the script again using the same command as in Step 5.

## Troubleshooting
- If you encounter any issues with the installation or running the script, ensure that all dependencies are installed correctly and that Python is added to your system PATH.
- For any audio-related issues, make sure that your microphone is working properly and that the correct audio input device is selected.

## Additional Notes
- The script uses Whisper for voice recognition and PyAudio for real-time audio capture.
- The trigger phrase and Minecraft command can be customized using the command-line arguments `--trigger` and `--command`.
- The duration for listening can be set using the `--duration` argument.

By following these instructions, you should be able to set up and run the Voice Command Listener for Minecraft on your Windows machine. If you have any questions or need further assistance, please refer to the official documentation for the libraries used or seek help from the respective communities.