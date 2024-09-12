import json
import importlib
import os
import sys

class CommandFactory:
    def __init__(self, api_url):
        self.api_url = api_url
        self.commands = self.load_commands()
        self.loaded_classes = self.load_command_classes()

        # Get the absolute path to the 'commands' directory
        commands_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))

        # Add the absolute path of 'commands' directory to the Python path
        sys.path.append(commands_path)

    def load_commands(self):
        """Load commands from commands.json."""
        try:
            with open('commands.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("commands.json file not found.")
            return {}

    def load_command_classes(self):
        """Load the command classes dynamically from features.txt."""
        classes = {}
        try:
            with open('features.txt', 'r') as file:
                for line in file:
                    class_name = line.strip()  # Get the class name from the line
                    if class_name:
                        # Add 'commands.' prefix with the correct CamelCase module name
                        module_name = f"commands.{class_name}"

                        try:
                            # Import module with CamelCase
                            module = importlib.import_module(module_name)

                            # Access the class from the module
                            command_class = getattr(module, class_name)

                            # Store the class for later use
                            classes[class_name] = command_class
                        except (ModuleNotFoundError, AttributeError) as e:
                            print(f"Error loading {class_name} from module {module_name}: {e}")
        except FileNotFoundError:
            print("features.txt file not found.")
        return classes

    def get_command(self, command_input):
        """Determine and return an instance of the command class based on input."""
        parts = command_input.split()
        command_key = parts[0]
        command_config = self.commands.get(command_key)

        if not command_config:
            print(f"Command {command_key} not recognized.")
            return None

        # Get the class name from the commands.json binding
        class_key = command_config['class']
        command_class = self.loaded_classes.get(class_key)

        if not command_class:
            print(f"Class {class_key} not found in loaded classes.")
            return None

        # Check if command requires parameters
        requires_parameter = getattr(command_class, 'requires_parameter', False)
        requires_username = getattr(command_class, 'requires_username', False)
        parameter = " ".join(parts[1:]) if len(parts) > 1 else None

        if requires_parameter and not parameter:
            print(f"{command_key} command requires a parameter.")
            return None

        if requires_username and not parameter:
            # Use the command class's method to fetch the username
            parameter = command_class.get_username_from_file()  
            if not parameter:
                print(f"{command_key} command requires a username.")
                return None

        # Instantiate command class with or without parameters
        if command_class.requires_api:
            if requires_username:
                return command_class(self.api_url, parameter)
            return command_class(self.api_url, parameter) if parameter else command_class(self.api_url)
        else:
            return command_class(parameter) if parameter else command_class()

if __name__ == "__main__":
    factory = CommandFactory("https://graphql.anilist.co")
    while True:
        command_input = input("Enter command: ").strip()
        if command_input == "quit":
            print("Exiting...")
            break
        command = factory.get_command(command_input)
        if command:
            command.execute()
        else:
            print("No command found for input.")
