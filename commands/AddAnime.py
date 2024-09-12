import requests
import json

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

        anime_id = self.find_anime_id(self.anime_name)
        if anime_id:
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

                # Check for duplicates in "watched_anime.txt" before writing
                try:
                    with open('watched_anime.txt', 'r') as file:
                        watched_list = file.readlines()
                        watched_list = [line.strip() for line in watched_list]
                except FileNotFoundError:
                    watched_list = []

                anime_entry = f"{self.anime_name}: {rating}"

                if anime_entry not in watched_list:
                    try:
                        with open('watched_anime.txt', 'a') as file:
                            file.write(f"{anime_entry}\n")  # Ensure new line is added with \n
                        print(f"Added '{self.anime_name}' to watched_anime.txt.")
                    except IOError as e:
                        print(f"Failed to write to watched_anime.txt: {e}")
                else:
                    print(f"'{self.anime_name}' already exists in watched_anime.txt.")
            else:
                print(f"Failed to mark '{self.anime_name}' as completed. HTTP Status: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"Anime '{self.anime_name}' not found.")

    def find_anime_id(self, anime_name):
        query = '''
        query ($name: String) {
            Media (search: $name, type: ANIME) {
                id
            }
        }
        '''
        variables = {'name': anime_name}
        response = requests.post(self.api_url, json={'query': query, 'variables': variables}, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data['data']['Media']:
                return data['data']['Media']['id']
            else:
                print("No anime found with that name.")
                return None
        else:
            print(f"Failed to search for anime. HTTP Status: {response.status_code}")
            return None
