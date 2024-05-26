from mcrcon import MCRcon

def send_command(command):
    with MCRcon("localhost", "Throwawaypassword-1", port=25575) as mcr:
        response = mcr.command(command)
        print(response)

if __name__ == "__main__":
    while True:
        command = input("Enter command to send to Minecraft server: ")
        send_command(command)
