import sounddevice as sd
import numpy as np
import subprocess
import argparse
import tkinter as tk
from tkinter import ttk
import threading
from mcrcon import MCRcon
import speech_recognition as sr

# Initialize the recognizer
recognizer = sr.Recognizer()

print("Listening for the trigger phrase...")

# Global variable to control listening
listening = False

# Function to process audio and detect trigger phrase
def listen_for_trigger(trigger_phrase, minecraft_command):
    global listening
    while listening:
        # Capture audio data from the microphone
        with sr.Microphone() as source:
            print("Microphone is ready. Listening...")
            audio_data = recognizer.listen(source)

        try:
            # Transcribe audio using Google Speech Recognition
            result = recognizer.recognize_google(audio_data)
            print("You said: " + result)

            # Check if the trigger phrase is detected
            if trigger_phrase.lower() in result.lower():
                print("Trigger phrase detected! Executing command...")
                execute_minecraft_command(minecraft_command)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Function to execute the Minecraft command using mcrcon
def execute_minecraft_command(command):
    try:
        with MCRcon("localhost", "Throwawaypassword-1", port=25575) as mcr:
            response = mcr.command(command)
            print("Command Response:", response)
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

# Start the Tkinter event loop
root.mainloop()
