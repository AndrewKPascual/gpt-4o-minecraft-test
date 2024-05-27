import os
import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = 'gpt-4'

# Define the custom Minecraft command tool
class MinecraftCommandTool:
    def run_command(self, command):
        # Implement the logic to run the Minecraft command on the server
        # This is a placeholder implementation
        print(f"Running Minecraft command: {command}")
        return f"Command '{command}' executed successfully on the Minecraft server."

# Instantiate the custom tool
minecraft_tool = MinecraftCommandTool()

# Define agents with new roles and prompts
input_agent = Agent(
    role='User Input Handler',
    goal='Receive a command input from the user and ensure it is formatted correctly for Minecraft.',
    backstory="""You are responsible for taking user input and preparing it for execution as a Minecraft command.
                 Ensure the input is valid and well-formed, ready for execution. Note: Commands should not start with '/'
                 as it is perceived to be at the start already.""",
    verbose=True,
    allow_delegation=False
)

executor_agent = Agent(
    role='Minecraft Command Executor',
    goal='Execute the formatted Minecraft command on the server using the custom tool.',
    backstory="""You specialize in executing commands on a Minecraft server.
                 Using the MinecraftCommandTool, you ensure commands are executed promptly and accurately.""",
    verbose=True,
    allow_delegation=False,
    tools=[minecraft_tool]
)

# Define tasks with a specific focus on handling and executing Minecraft commands
task1 = Task(
    description="""Receive a command input from the user. Validate and format it as needed for Minecraft execution.
                   Note: Commands should not start with '/' as it is perceived to be at the start already.""",
    expected_output="A well-formed Minecraft command ready for execution",
    agent=input_agent
)

task2 = Task(
    description="""Execute the formatted Minecraft command using the MinecraftCommandTool.""",
    expected_output="Confirmation of the command execution and its result",
    agent=executor_agent
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[input_agent, executor_agent],
    tasks=[task1, task2],
    verbose=2
)

# Get your crew to work and save the results
result = crew.kickoff()
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
with open(f"Minecraft_Command_Execution_Report_{timestamp}.txt", "w") as file:
    file.write(result)

print("######################")
print("Results saved in:", f"Minecraft_Command_Execution_Report_{timestamp}.txt")
print(result)
