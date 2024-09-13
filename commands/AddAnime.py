import requests
import json
import os

class AddAnime:
    requires_api = True  # Indicates this command needs the API URL
    requires_parameter = True  # Indicates this command requires a parameter

    def __init__(self, api_url, anime_name):
        if not anime_name:
            raise ValueError("Anime name is required for AddAnime command.")
        self.api_url = api_url
        self.headers = self.get_headers()
        self.anime_name = anime_name

    @staticmethod
    def get_headers():
        token = AddAnime.get_api_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    @staticmethod
    def get_api_token():
        """Static method to retrieve the API token from a file."""
        try:
            with open('token.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Token file not found.")
            return None

    def execute(self):
        """Method to execute the addition of anime to the watchlist."""
        if not self.anime_name:
            print("Anime name not specified.")
            return

        # Step 1: Search for the anime by name
        anime_id = self.find_anime_id(self.anime_name)
        if anime_id:
            # Step 2: Ask the user which list to add it to
            print("What list do you want to add it to?")
            print("1. Completed")
            print("2. Currently watching")
            print("3. On hold")
            print("4. Dropped")
            print("5. Plan to watch")

            list_choice = input("Enter the number of your choice: ")
            if list_choice == '1':
                # Step 3: Handle completed anime (with rating)
                self.add_to_completed(anime_id)
            else:
                # Step 4: Handle other lists (with progress tracking)
                self.add_to_other_list(anime_id, list_choice)
        else:
            print(f"Anime '{self.anime_name}' not found.")

    def add_to_completed(self, anime_id):
        """Adds the anime to the 'Completed' list with a rating."""
        rating = input("Enter your rating for the anime (1-10): ")
        try:
            rating = int(rating)
            if not 1 <= rating <= 10:
                raise ValueError("Rating must be between 1 and 10.")
        except ValueError as e:
            print(e)
            return

        mutation = '''
        mutation ($mediaId: Int, $score: Float) {
            SaveMediaListEntry(mediaId: $mediaId, status: COMPLETED, score: $score) {
                id
            }
        }
        '''
        variables = {
            'mediaId': anime_id,
            'score': float(rating)
        }

        response = requests.post(self.api_url, json={'query': mutation, 'variables': variables}, headers=self.headers)
        if response.status_code == 200:
            print(f"Marked '{self.anime_name}' as completed with a rating of {rating}.")
            self.remove_from_other_lists('watched_anime.txt')
            self.save_to_watched_list(rating)
        else:
            print(f"Failed to mark '{self.anime_name}' as completed. HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")

    def add_to_other_list(self, anime_id, list_choice):
        """Adds the anime to one of the other lists (Currently Watching, On Hold, etc.) with progress tracking."""
        episode_count = input("How many episodes have you watched? ")

        try:
            episode_count = int(episode_count)
        except ValueError:
            print("Episode count must be a number.")
            return

        # Mapping list_choice to API status and corresponding file
        status_mapping = {
            '2': ('CURRENT', 'currently_watching.txt'),  # Currently watching
            '3': ('PAUSED', 'on_hold.txt'),   # On hold
            '4': ('DROPPED', 'dropped.txt'),  # Dropped
            '5': ('PLANNING', 'plan_to_watch.txt')  # Plan to watch
        }

        status, filename = status_mapping.get(list_choice)

        if not status:
            print("Invalid choice. Please select a valid option.")
            return

        mutation = '''
        mutation ($mediaId: Int, $status: MediaListStatus, $progress: Int) {
            SaveMediaListEntry(mediaId: $mediaId, status: $status, progress: $progress) {
                id
            }
        }
        '''
        variables = {
            'mediaId': anime_id,
            'status': status,
            'progress': episode_count
        }

        response = requests.post(self.api_url, json={'query': mutation, 'variables': variables}, headers=self.headers)
        if response.status_code == 200:
            print(f"Marked '{self.anime_name}' as {status.lower()} with {episode_count} episodes watched.")
            # Remove from other lists before adding to the new list
            self.remove_from_other_lists(filename)
            self.save_to_list_file(filename, episode_count)
        else:
            print(f"Failed to update list for '{self.anime_name}'. HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")

    def save_to_watched_list(self, rating):
        """Check for duplicates in 'watched_anime.txt' before writing."""
        self.save_to_file('watched_anime.txt', f"{self.anime_name}: {rating}")

    def save_to_list_file(self, filename, episode_count):
        """Check for duplicates and save anime to the specified list file with episode count."""
        self.save_to_file(filename, f"{self.anime_name}: {episode_count} episodes")

    def save_to_file(self, filename, entry):
        """General method to check for duplicates in a file before writing an entry."""
        try:
            with open(filename, 'r') as file:
                entry_list = file.readlines()
                # Normalize the entries: strip whitespace, convert to lowercase
                entry_list = [line.strip().lower() for line in entry_list]
        except FileNotFoundError:
            entry_list = []

        # Normalize the anime name (lowercase for comparison)
        anime_entry_clean = f"{self.anime_name}".strip().lower()

        # Check if anime exists in the list file (ignore episode count or rating during check)
        if any(anime_entry_clean in entry for entry in entry_list):
            print(f"'{self.anime_name}' already exists in {filename}.")
        else:
            try:
                with open(filename, 'a') as file:
                    file.write(f"{entry}\n")  # Ensure new line is added with \n
                print(f"Added '{self.anime_name}' to {filename}.")
            except IOError as e:
                print(f"Failed to write to {filename}: {e}")

    def remove_from_other_lists(self, current_list_file):
        """Removes the anime from other list files if it exists."""
        # List of all possible list files
        list_files = ['currently_watching.txt', 'on_hold.txt', 'dropped.txt', 'plan_to_watch.txt']

        # Check if the current_list_file is in the list before removing it
        if current_list_file in list_files:
            list_files.remove(current_list_file)

        # Normalize the anime name for comparison
        anime_entry_clean = f"{self.anime_name}".strip().lower()

        for file_name in list_files:
            if os.path.exists(file_name):
                try:
                    with open(file_name, 'r') as file:
                        lines = file.readlines()

                    # Filter out lines that contain the anime entry
                    new_lines = [line for line in lines if anime_entry_clean not in line.strip().lower()]

                    # If the file was modified (i.e., anime was found and removed), update it
                    if len(new_lines) < len(lines):
                        with open(file_name, 'w') as file:
                            file.writelines(new_lines)
                        print(f"Removed '{self.anime_name}' from {file_name}.")
                except IOError as e:
                    print(f"Failed to update {file_name}: {e}")

    def find_anime_id(self, anime_name):
        """Searches for the anime by name and returns its ID."""
        query = '''
        query ($name: String) {
            Media (search: $name, type: ANIME) {
                id
                title {
                    romaji
                    english
                }
            }
        }
        '''
        variables = {'name': anime_name}
        response = requests.post(self.api_url, json={'query': query, 'variables': variables}, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data['data']['Media']:
                anime = data['data']['Media']
                print(f"Found anime: {anime['title']['romaji']} (ID: {anime['id']})")
                return anime['id']
            else:
                print("No anime found with that name.")
                return None
        else:
            print(f"Failed to search for anime. HTTP Status: {response.status_code}")
            return None
