import sounddevice as sd
import numpy as np
import subprocess
import argparse
import threading
from mcrcon import MCRcon
import speech_recognition as sr
import whisper
from minecraft_ai_tool import MinecraftAITool

# Initialize the recognizer
recognizer = sr.Recognizer()

# Load the Whisper model
model = whisper.load_model("base")

print("Listening for the trigger phrase...")

# Global variable to control listening
listening = False

# Function to process audio and detect trigger phrase
def listen_for_trigger(trigger_phrase, minecraft_command):
    global listening
    # Create an instance of MinecraftAITool
    tool = MinecraftAITool(host="localhost", port=25575, password="your_password")
    tool.connect_to_server()

    while listening:
        # Capture audio data from the microphone
        with sr.Microphone() as source:
            print("Microphone is ready. Listening...")
            audio_data = recognizer.listen(source)

        try:
            # Transcribe audio using Whisper
            audio_np = np.frombuffer(audio_data.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0
            result = model.transcribe(audio_np)
            transcription = result["text"]
            print("You said: " + transcription)

            # Check if the trigger phrase is detected
            if trigger_phrase.lower() in transcription.lower():
                print("Trigger phrase detected! Executing command...")
                response = tool.handle_voice_command(transcription)
                print("Command Response:", response)
        except Exception as e:
            print("An error occurred during transcription:", str(e))

    tool.disconnect_from_server()

# Function to execute the Minecraft command using mcrcon
def execute_minecraft_command(command):
    try:
        with MCRcon("localhost", "Throwawaypassword-1", port=25575) as mcr:
            response = mcr.command(command)
            print("Command Response:", response)
    except Exception as e:
        print("An error occurred while executing the command:", str(e))

# Function to start the listener
def start_listener(trigger_phrase, minecraft_command, duration):
    global listening
    listening = True
    print(f"Starting listener for {duration} seconds with trigger phrase '{trigger_phrase}' and command '{minecraft_command}'")
    listener_thread = threading.Thread(target=listen_for_trigger, args=(trigger_phrase, minecraft_command))
    listener_thread.start()
    listener_thread.join(timeout=duration)
    listening = False
    print("Stopped listening.")

# Main function to run the listener
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice Command Listener for Minecraft")
    parser.add_argument("--trigger", type=str, required=True, help="Trigger phrase to listen for")
    parser.add_argument("--command", type=str, required=True, help="Minecraft command to execute")
    parser.add_argument("--duration", type=int, default=30, help="Duration to listen for in seconds")
    args = parser.parse_args()

    start_listener(args.trigger, args.command, args.duration)
