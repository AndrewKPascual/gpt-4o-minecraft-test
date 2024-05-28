import sounddevice as sd
import numpy as np
import subprocess
import argparse
import tkinter as tk
from tkinter import ttk
import threading
from mcrcon import MCRcon
import whisper
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Initialize the Whisper model
model = whisper.load_model("base")

print("Listening for the trigger phrase...")

# Global variable to control listening
listening = False

# Function to process audio and detect trigger phrase
def listen_for_trigger(trigger_phrase, minecraft_command):
    global listening

    # Initialize ChatMessageHistory
    chat_history = ChatMessageHistory()

    # Define a Runnable to process the transcribed text
    def process_transcribed_text(text):
        # Process the transcribed text with LangChain
        langchain_response = LangChain.process(text)
        print("LangChain response: " + langchain_response)

        # Check if the trigger phrase is detected
        if trigger_phrase.lower() in langchain_response.lower():
            print("Trigger phrase detected! Executing command...")
            execute_minecraft_command(minecraft_command)

    # Wrap the Runnable with RunnableWithMessageHistory
    runnable_with_history = RunnableWithMessageHistory(process_transcribed_text, chat_history)

    while listening:
        # Capture audio data from the microphone
        print("Microphone is ready. Listening...")
        audio_data = sd.rec(int(16000 * 5), samplerate=16000, channels=1, dtype='int16')
        sd.wait()

        try:
            # Convert audio data to float32
            audio_data = audio_data.astype(np.float32) / 32768.0

            # Transcribe audio using Whisper
            result = model.transcribe(np.squeeze(audio_data))
            print("You said: " + result['text'])

            # Process the transcribed text with the RunnableWithMessageHistory
            runnable_with_history(result['text'])
        except Exception as e:
            print("An error occurred during transcription or LangChain processing:", str(e))

# Function to execute the Minecraft command using mcrcon
def execute_minecraft_command(command):
    try:
        # Check if the Minecraft server is accessible
        with MCRcon("localhost", "Throwawaypassword-1", port=25575) as mcr:
            print("Successfully connected to the Minecraft server.")
            response = mcr.command(command)
            print("Command Response:", response)
    except ConnectionRefusedError:
        print("Connection to the Minecraft server was refused. Please ensure the server is running and accessible.")
    except Exception as e:
        print("An error occurred while executing the command:", str(e))

# Function to start the listener
def start_listener():
    global listening
    listening = True
    trigger_phrase = trigger_entry.get()
    minecraft_command = command_entry.get()
    duration = int(duration_entry.get())
    print(f"Starting listener for {duration} seconds with trigger phrase '{trigger_phrase}' and command '{minecraft_command}'")
    listener_thread = threading.Thread(target=listen_for_trigger, args=(trigger_phrase, minecraft_command))
    listener_thread.start()

# Function to stop the listener
def stop_listener():
    global listening
    listening = False
    print("Stopped listening.")

# Commenting out the default microphone information print statement
# print("Default microphone info:", sd.query_devices(kind='input'))

# Function to test Minecraft command execution
def test_minecraft_command_execution():
    test_command = "time set day"
    print("Testing Minecraft command execution with command:", test_command)
    execute_minecraft_command(test_command)

# Create the main window
root = tk.Tk()
root.title("Voice Command Listener for Minecraft")

# Create and place the widgets
ttk.Label(root, text="Trigger Phrase:").grid(column=0, row=0, padx=10, pady=5)
trigger_entry = ttk.Entry(root, width=30)
trigger_entry.grid(column=1, row=0, padx=10, pady=5)
trigger_entry.insert(0, "execute command")

ttk.Label(root, text="Minecraft Command:").grid(column=0, row=1, padx=10, pady=5)
command_entry = ttk.Entry(root, width=30)
command_entry.grid(column=1, row=1, padx=10, pady=5)
command_entry.insert(0, "/give @p diamond 1")

ttk.Label(root, text="Duration (seconds):").grid(column=0, row=2, padx=10, pady=5)
duration_entry = ttk.Entry(root, width=30)
duration_entry.grid(column=1, row=2, padx=10, pady=5)
duration_entry.insert(0, "30")

start_button = ttk.Button(root, text="Start Listening", command=start_listener)
start_button.grid(column=0, row=3, padx=10, pady=10)

stop_button = ttk.Button(root, text="Stop Listening", command=stop_listener)
stop_button.grid(column=1, row=3, padx=10, pady=10)

# Add a button to test Minecraft command execution
test_button = ttk.Button(root, text="Test Command Execution", command=test_minecraft_command_execution)
test_button.grid(column=0, row=4, columnspan=2, padx=10, pady=10)

# Directly call the test function on startup to bypass the GUI for testing
test_minecraft_command_execution()

# Start the Tkinter event loop
root.mainloop()
