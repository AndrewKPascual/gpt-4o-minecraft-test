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
from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnableSequence

# Global variable to store chat message history
store = {}

# Function to get or create a chat message history based on session_id
def get_session_history(session_id: str) -> ChatMessageHistory:
    # For simplicity, we use an in-memory implementation
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

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
        # Define the logic for processing the transcribed text using a language model
        def langchain_logic(input_text):
            try:
                print(f"LangChain logic input: {input_text}", flush=True)
                # Simulate LLM processing step using RunnableLambda
                def simulate_llm_processing(text):
                    # Simulate a response from the LLM
                    return {"message": f"Simulated LLM response to: {text}"}

                llm_runnable = RunnableLambda(simulate_llm_processing)

                # Define a second RunnableLambda to log the response
                def log_response(response):
                    print(f"Logging response: {response['message']}", flush=True)
                    return response

                log_runnable = RunnableLambda(log_response)

                # Create a RunnableSequence with the LLM runnable and the log runnable
                runnable_sequence = RunnableSequence(llm_runnable, log_runnable)

                # Process the input text using the RunnableSequence
                response = runnable_sequence.invoke(input_text)
                print(f"LangChain logic output: {response}", flush=True)
                return response
            except Exception as e:
                print("An error occurred during LangChain processing:", str(e), flush=True)
                return {"message": ""}

        # Function to determine the appropriate Minecraft command based on the transcribed text
        def determine_minecraft_command(transcribed_text):
            # Example logic to determine the command based on keywords in the transcribed text
            if "give diamond" in transcribed_text.lower():
                return "/give @p diamond 1"
            elif "set time day" in transcribed_text.lower():
                return "time set day"
            # Add more conditions as needed
            else:
                return ""

        # Create a RunnableLambda for the LangChain logic
        langchain_runnable = RunnableLambda(langchain_logic)

        # Process the transcribed text with the LangChain runnable
        langchain_response = langchain_runnable.invoke(text)
        print("LangChain response: " + langchain_response['message'], flush=True)

        # Determine the appropriate Minecraft command based on the transcribed text
        minecraft_command = determine_minecraft_command(langchain_response['message'])

        # Check if the trigger phrase is detected
        if trigger_phrase.lower() in langchain_response['message'].lower():
            print("Trigger phrase detected! Executing command...", flush=True)
            response = minecraft_command_tool(minecraft_command)
            print("Command Response:", response, flush=True)

    # Convert the function into a Runnable object
    runnable = RunnableLambda(process_transcribed_text)

    # Wrap the Runnable with RunnableWithMessageHistory
    runnable_with_history = RunnableWithMessageHistory(runnable, get_session_history=get_session_history)

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
            print(f"Invoking RunnableWithMessageHistory with text: {result['text']} and config: {{'configurable': {{'session_id': 'default_session'}}}}", flush=True)
            try:
                response = runnable_with_history.invoke(result['text'], config={"configurable": {"session_id": "default_session"}})
                print(f"RunnableWithMessageHistory response: {response}", flush=True)
            except Exception as e:
                print("An error occurred during RunnableWithMessageHistory invocation:", str(e), flush=True)
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

# Define a custom tool to execute Minecraft commands
@tool
def minecraft_command_tool(command: str) -> str:
    """
    Executes a Minecraft command using mcrcon and returns the response.
    """
    try:
        with MCRcon("localhost", "Throwawaypassword-1", port=25575) as mcr:
            response = mcr.command(command)
            return response
    except ConnectionRefusedError:
        return "Connection to the Minecraft server was refused. Please ensure the server is running and accessible."
    except Exception as e:
        return f"An error occurred while executing the command: {str(e)}"

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

# Function to test the integration with simulated input
def test_integration_with_simulated_input():
    trigger_phrase = "execute command"
    minecraft_command = "/give @p diamond 1"
    simulated_transcribed_text = "execute command to give diamond"

    # Initialize ChatMessageHistory
    chat_history = ChatMessageHistory()

    # Define a Runnable to process the transcribed text
    def process_transcribed_text(text):
        # Define the logic for processing the transcribed text using a language model
        def langchain_logic(input_text):
            try:
                # Simulate LLM processing step using RunnableLambda
                def simulate_llm_processing(text):
                    # Simulate a response from the LLM
                    return {"message": f"Simulated LLM response to: {text}"}

                llm_runnable = RunnableLambda(simulate_llm_processing)

                # Define a second RunnableLambda to log the response
                def log_response(response):
                    print(f"Logging response: {response['message']}")
                    return response

                log_runnable = RunnableLambda(log_response)

                # Create a RunnableSequence with the LLM runnable and the log runnable
                runnable_sequence = RunnableSequence(llm_runnable, log_runnable)

                # Process the input text using the RunnableSequence
                response = runnable_sequence.invoke(input_text)
                return response
            except Exception as e:
                print("An error occurred during LangChain processing:", str(e))
                return {"message": ""}

        # Create a RunnableLambda for the LangChain logic
        langchain_runnable = RunnableLambda(langchain_logic)

        # Process the transcribed text with the LangChain runnable
        langchain_response = langchain_runnable.invoke(text)
        print("LangChain response: " + langchain_response['message'])

        # Check if the trigger phrase is detected
        if trigger_phrase.lower() in langchain_response['message'].lower():
            print("Trigger phrase detected! Executing command...")
            execute_minecraft_command(minecraft_command)


    # Convert the function into a Runnable object
    runnable = RunnableLambda(process_transcribed_text)

    # Wrap the Runnable with RunnableWithMessageHistory
    runnable_with_history = RunnableWithMessageHistory(runnable, get_session_history=get_session_history)

    # Simulate the processing of the transcribed text
    print(f"Invoking RunnableWithMessageHistory with text: {simulated_transcribed_text} and config: {{'configurable': {{'session_id': 'default_session'}}}}")
    runnable_with_history.invoke(simulated_transcribed_text, config={"configurable": {"session_id": "default_session"}})

# Directly call the test function on startup to bypass the GUI for testing
test_integration_with_simulated_input()

# Start the Tkinter event loop
root.mainloop()
