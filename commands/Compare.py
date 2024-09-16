import requests
import json
import unicodedata
from rapidfuzz import process, fuzz  # Correct import for rapidfuzz
import os

class Compare:
    requires_api = True
    requires_parameter = True

    def __init__(self, api_url, username=None):
        if not username:
            raise ValueError("Username is required for Compare.")
        self.api_url = api_url
        self.username = username
        self.headers = self.get_headers()

    @staticmethod
    def get_headers():
        token = Compare.get_api_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    @staticmethod
    def get_api_token():
        try:
            with open('token.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Token file not found.")
            return None

    def execute(self):
        if self.username:
            user_data = self.fetch_user_completed_anime(self.username)
            if user_data and 'data' in user_data and 'MediaListCollection' in user_data['data']:
                self._display_stats(user_data['data']['MediaListCollection'])
                self.compare_watched_list(user_data['data']['MediaListCollection'])
            else:
                print(f"No data available for {self.username}.")
        else:
            print("Username is required for this command.")

    def fetch_user_completed_anime(self, username):
        query = """
        query ($userName: String, $status: MediaListStatus) {
          MediaListCollection(userName: $userName, status: $status, type: ANIME) {
            lists {
              name
              entries {
                media {
                  id
                  title {
                    romaji
                  }
                }
              }
            }
          }
        }
        """
        variables = {"userName": username, "status": "COMPLETED"}
        response = requests.post(self.api_url, json={"query": query, "variables": variables}, headers=self.headers)
        
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                print("Failed to decode JSON from response.")
                return None
        elif response.status_code == 404:
            try:
                error_details = response.json()
                if error_details['errors'][0]['message'] == "Private User":
                    print(f"User's profile is set to private.")
                else:
                    print(f"Failed to fetch user stats for {username}: {response.status_code}")
                    print("Error details:", json.dumps(error_details, indent=4))
            except json.JSONDecodeError:
                print("Failed to decode JSON from response.")
            return None
        else:
            print(f"Failed to fetch user stats for {username}: {response.status_code}")
            print("Response content:", response.content)
            return None

    def _display_stats(self, media_list_collection):
        if not media_list_collection or 'lists' not in media_list_collection:
            print("Media list collection is empty or malformed.")
            return
        
        total_animes_watched = 0
        for anime_list in media_list_collection['lists']:
            if 'completed' in anime_list['name'].lower():
                total_animes_watched += len(anime_list['entries'])

        print(f"Total Animes Watched: {total_animes_watched}")

    def compare_watched_list(self, media_list_collection):
        # Ensure compare.txt exists
        if not os.path.exists('compare.txt'):
            open('compare.txt', 'w', encoding='utf-8').close()

        if not media_list_collection or 'lists' not in media_list_collection:
            print("Media list collection is empty or malformed.")
            return

        user1_watched_titles = self.read_user1_watched_list()
        normalized_user1_watched = {self.normalize_string(title) for title in user1_watched_titles}

        completed_anime_romaji = []
        for anime_list in media_list_collection['lists']:
            if 'completed' in anime_list['name'].lower():
                completed_anime_romaji.extend([entry['media']['title']['romaji'] for entry in anime_list['entries']])

        fetched_anime_count = len(completed_anime_romaji)
        total_animes_watched = fetched_anime_count

        print(f"Fetched {fetched_anime_count} completed anime.")

        # Use the optimized set operations and fuzzy matching in all cases
        # Convert completed_anime_romaji to a set for fast membership checking
        completed_anime_set = {self.normalize_string(title) for title in completed_anime_romaji}

        # Find differences using set difference
        exact_difference_titles = list(completed_anime_set - normalized_user1_watched)

        # Fuzzy match for titles that didn't match exactly
        difference_titles = [
            title for title in exact_difference_titles
            if not self.fuzzy_match(title, normalized_user1_watched)
        ]

        if len(difference_titles) >= 21:
            user_input = input(f"{self.username} has {len(difference_titles)} animes you haven't seen. "
                               "Do you want to dump the list to compare.txt? (yes/no): ").strip().lower()
            if user_input == 'yes':
                # Open file with utf-8 encoding
                with open('compare.txt', 'w', encoding='utf-8') as file:
                    file.write("\n".join(difference_titles))
                print("compare.txt has been updated.")
            else:
                print(f"{self.username} has {len(difference_titles)} animes you haven't seen, here is the list:")
                for title in difference_titles:
                    print(f"- {title}")
        else:
            print(f"{self.username} has {len(difference_titles)} animes you haven't seen, here is the list:")
            for title in difference_titles:
                print(f"- {title}")

    def read_user1_watched_list(self):
        try:
            with open('watched_anime.txt', 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print("watched_anime.txt file not found.")
            return []

    def normalize_string(self, title):
        title = unicodedata.normalize('NFKC', title)
        title = title.lower()
        title = title.replace('×', 'x')
        return ' '.join(title.split())

    def fuzzy_match(self, title, normalized_titles):
        # Use rapidfuzz for fast fuzzy matching
        normalized_title = self.normalize_string(title)
        matches = process.extract(normalized_title, normalized_titles, limit=1, scorer=fuzz.ratio)
        if matches and matches[0][1] > 80:  # Match found with a ratio greater than 80
            return True
        return False
