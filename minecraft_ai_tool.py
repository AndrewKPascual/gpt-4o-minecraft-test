import json
from mcrcon import MCRcon
from langchain import OpenAI, ConversationChain
from langchain.memory import ConversationBufferMemory

class MinecraftAITool:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.chat_history = []
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=OpenAI(temperature=0),
            memory=self.memory,
        )

    def connect_to_server(self):
        self.mcr = MCRcon(self.host, self.port, self.password)
        self.mcr.connect()

    def disconnect_from_server(self):
        self.mcr.disconnect()

    def execute_command(self, command):
        response = self.mcr.command(command)
        return response

    def add_to_chat_history(self, message):
        self.chat_history.append(message)

    def get_chat_history(self):
        return self.chat_history

    def process_voice_command(self, voice_command):
        # Use langchain to process the voice command and convert it to a Minecraft command
        response = self.conversation.predict(input=voice_command)
        if "give me a diamond" in response.lower():
            minecraft_command = "/give @p diamond 1"
        else:
            minecraft_command = f"/say {response}"
        return minecraft_command

    def handle_voice_command(self, voice_command):
        # Add the voice command to chat history
        self.add_to_chat_history(voice_command)

        # Process the voice command to get the Minecraft command
        minecraft_command = self.process_voice_command(voice_command)

        # Execute the Minecraft command
        response = self.execute_command(minecraft_command)

        # Return the response from the server
        return response

# Example usage
if __name__ == "__main__":
    tool = MinecraftAITool(host="localhost", port=25575, password="your_password")
    tool.connect_to_server()
    response = tool.handle_voice_command("give me a diamond")
    print("Server response:", response)
    tool.disconnect_from_server()
