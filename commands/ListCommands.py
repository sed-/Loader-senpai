import json

class ListCommands:
    requires_api = False         # Indicates this command needs the API URL
    requires_parameter = False   # Indicates this command does not necessarily require a parameter

    def __init__(self):
        self.commands_file = 'commands.json'
        self.excluded_commands = ['commands', 'features']  # List of commands to exclude

    def execute(self):
        """Loads the commands from the JSON file and prints them, excluding certain entries."""
        try:
            with open(self.commands_file, 'r') as file:
                commands = json.load(file)
                
            print("Available Commands:")
            for command, details in commands.items():
                if command in self.excluded_commands:
                    continue  # Skip the excluded commands
                if isinstance(details, dict) and 'description' in details:
                    print(f"{command}: {details['description']}")
        except FileNotFoundError:
            print("Commands file not found.")
        except json.JSONDecodeError:
            print("Error decoding commands file.")
