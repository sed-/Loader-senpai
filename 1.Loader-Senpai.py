import os
from command_factory import CommandFactory
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

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
        # Notify the user to put their token and run -ulist command
        print(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}: {Fore.LIGHTCYAN_EX}Hey {Fore.LIGHTGREEN_EX}{username}{Fore.WHITE}, {Fore.LIGHTCYAN_EX}your watched anime list is empty!{Fore.WHITE}")
        print(f"{Fore.LIGHTBLACK_EX}Loader{Fore.WHITE}-{Fore.LIGHTYELLOW_EX}senpai{Fore.WHITE}: {Fore.LIGHTCYAN_EX}Please put your token in token.txt and run the {Fore.LIGHTGREEN_EX}-ulist{Fore.LIGHTCYAN_EX} command to update your watched list.")
        return False  # Watched anime list is not present

if __name__ == "__main__":
    # Get the username from the file or ask the user
    username = get_username()

    # Check the token file and proceed accordingly
    token_present = check_token(username)

    # Check the watched_anime.txt file and prompt the user if it's empty
    watched_anime_present = check_watched_anime(username)

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
