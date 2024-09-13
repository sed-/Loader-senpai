import os
import platform
import requests
import re
import unicodedata
from command_factory import CommandFactory
from colorama import Fore, Style, init


# Initialize colorama
init(autoreset=True)

# Get the current PID
pid = str(os.getpid())

# Define the path to pid.txt
pid_file_path = 'pid.txt'

# Check if pid.txt exists
if os.path.exists(pid_file_path):
    # Read the existing PID
    with open(pid_file_path, 'r') as pid_file:
        existing_pid = pid_file.read().strip()
    if existing_pid != pid:
        # PIDs are different, update pid.txt
        with open(pid_file_path, 'w') as pid_file:
            pid_file.write(pid)
else:
    # pid.txt doesn't exist, create it and write the current PID
    with open(pid_file_path, 'w') as pid_file:
        pid_file.write(pid)

# Initialize colorama
init(autoreset=True)

# cd part of the code
def braaafile(filename, search_path="."):
    
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

try:
    
    filename = '1.Loader-Senpai.py'
    file_path = braaafile(filename)

    if file_path:
        directory = os.path.dirname(file_path)

        os.chdir(directory)

        print(f"File : {file_path} found ≧◡≦.")
    else:
        print("File not found. ༼ ﹏ ༽")
except Exception as e:
    print(f"An error occurred: {e} (˃̣̣̥⌓˂̣̣̥ )")

#cd part ends here 

# Define the API URL at the beginning of your script
API_URL = "https://graphql.anilist.co"

# Function to clear the screen
def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# Function to get the username from a file or prompt the user
def get_username():
    try:
        with open("username.txt", "r") as file:
            username = file.readline().strip()
            if not username:
                raise ValueError("Username is empty.")
            return username
    except (FileNotFoundError, ValueError):
        username = input(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}:{Fore.LIGHTCYAN_EX} What's your anilist.co user name? {Fore.WHITE}").strip()
        with open("username.txt", "w") as file:
            file.write(username)
        return username

# Function to check if token.txt is empty, and ask the user whether to open the readme in Notepad
def check_token(username):
    try:
        with open("token.txt", "r") as file:
            token = file.readline().strip()
            if not token:
                raise ValueError("Token is empty.")
            return True  # Token is present
    except (FileNotFoundError, ValueError):
        response = input(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}: {Fore.LIGHTCYAN_EX}Hey {Fore.LIGHTGREEN_EX}{username}{Fore.WHITE}, {Fore.LIGHTCYAN_EX}I noticed your token file is empty{Fore.WHITE}, {Fore.LIGHTCYAN_EX}do you want me to open the read me for setting this up{Fore.WHITE}?\n{Fore.GREEN}{username}{Fore.WHITE}: ").strip().lower()
        if response in ["yes", "y", "ya"]:
            try:
                # Open the !!Read me!!.txt file in Notepad (Windows)
                if os.name == 'nt':
                    os.system('notepad "!!Read me!!.txt"')
                else:
                    print(f"{Fore.RED}Notepad is not available on this system.")
                print(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}: {Fore.LIGHTCYAN_EX}Once you have put in your token, make sure to run -ulist to update your watched list.")
            except FileNotFoundError:
                print(f"{Fore.RED}!!Read me!!.txt file not found! Please check the file location.")
        # Continue without token regardless of response
        return False  # Token not present

# Function to check if watched_anime.txt is empty
def check_watched_anime(username):
    try:
        with open("watched_anime.txt", "r") as file:
            content = file.read().strip()
            if not content:
                raise ValueError("watched_anime.txt is empty.")
            return True  # Watched anime list is present
    except (FileNotFoundError, ValueError):
        print(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}: {Fore.LIGHTCYAN_EX}Hey {Fore.LIGHTGREEN_EX}{username}{Fore.WHITE}, {Fore.LIGHTCYAN_EX}your watched anime list is empty!{Fore.WHITE}")
        print(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}: {Fore.LIGHTCYAN_EX}Please put your token in token.txt and run the {Fore.LIGHTGREEN_EX}-ulist{Fore.LIGHTCYAN_EX} command to update your watched list.")
        return False  # Watched anime list is not present

# Function to check if dropped.txt exists
def check_dropped_file():
    try:
        with open("dropped.txt", "r") as file:
            return True  # dropped.txt exists
    except FileNotFoundError:
        print(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}: {Fore.LIGHTCYAN_EX}I noticed you're missing some files. Please type {Fore.LIGHTGREEN_EX}-ulist{Fore.LIGHTCYAN_EX} to get the missing files.")
        return False  # dropped.txt not present

if __name__ == "__main__":
    # Get the username from the file or ask the user
    username = get_username()

    # Check the token file and proceed accordingly
    token_present = check_token(username)

    # Check the watched_anime.txt file and prompt the user if it's empty
    watched_anime_present = check_watched_anime(username)

    # Check if dropped.txt is present, if not, prompt the user
    dropped_file_present = check_dropped_file()

    # Create an instance of CommandFactory with the necessary API URL
    factory = CommandFactory(api_url=API_URL)

    while True:
        # Prompt the user for a command
        command_input = input(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}:{Fore.LIGHTCYAN_EX} Whats up?\n{Fore.GREEN}{username}{Fore.WHITE}: ").strip()
        
        if command_input == "-r":
            clear_screen()
            continue
        elif command_input == "quit":
            print("Exiting program...")
            break

        # Use the factory to get and execute a command
        command = factory.get_command(command_input)
        if command:
            command.execute()
        else:
            print("Command not recognized.")
