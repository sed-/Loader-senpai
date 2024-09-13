import os
import requests

class ManualUpdate:
    requires_api = True
    requires_parameter = False
    requires_username = True

    def __init__(self, api_url, username=None):
        if not username:
            username = self.get_username_from_file()
            if not username:
                raise ValueError("Username is required for ManualUpdate.")
        self.api_url = api_url
        self.username = username
        self.headers = self.get_headers()
        self.existing_titles = self.load_existing_titles()

    @staticmethod
    def get_username_from_file():
        try:
            with open('username.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Username file not found.")
            return None

    @staticmethod
    def get_api_token():
        try:
            with open('token.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Token file not found.")
            return None

    def get_headers(self):
        token = self.get_api_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def load_existing_titles(self):
        try:
            with open('watched_anime.txt', 'r', encoding='utf-8') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            print("Completed titles file not found.")
            return set()

    def execute(self):
        query = """
        query ($userName: String) {
            MediaListCollection(userName: $userName, type: ANIME) {
                lists {
                    entries {
                        media {
                            title {
                                romaji
                            }
                        }
                        status
                    }
                }
            }
        }
        """
        variables = {'userName': self.username}
        response = requests.post(self.api_url, json={'query': query, 'variables': variables}, headers=self.headers)
        if response.status_code == 200:
            self.process_response(response.json())
        else:
            print("Failed to fetch data from API.")

    def process_response(self, json_response):
        if 'data' in json_response:
            categorized_titles = {
                'CURRENTLY_WATCHING': [],
                'ON_HOLD': [],
                'DROPPED': [],
                'PLAN_TO_WATCH': [],
                'COMPLETED': []
            }
            lists = json_response['data']['MediaListCollection']['lists']
            for list in lists:
                for entry in list['entries']:
                    status = entry['status']
                    title = entry['media']['title']['romaji']

                    if status == 'CURRENT':
                        categorized_titles['CURRENTLY_WATCHING'].append(title)
                    elif status == 'PLANNING':
                        categorized_titles['PLAN_TO_WATCH'].append(title)
                    elif status == 'PAUSED':
                        categorized_titles['ON_HOLD'].append(title)
                    elif status == 'DROPPED':
                        categorized_titles['DROPPED'].append(title)
                    elif status == 'COMPLETED':
                        categorized_titles['COMPLETED'].append(title)

            self.update_titles(categorized_titles)
        else:
            print("No useful data in response.")

    def update_titles(self, categorized_titles):
        file_mapping = {
            'CURRENTLY_WATCHING': 'currently_watching.txt',
            'ON_HOLD': 'on_hold.txt',
            'DROPPED': 'dropped.txt',
            'PLAN_TO_WATCH': 'plan_to_watch.txt',
            'COMPLETED': 'watched_anime.txt'
        }

        files_created = 0
        files_updated = 0
        total_animes_added = 0

        for category, titles in categorized_titles.items():
            file_name = file_mapping[category]
            titles_set = set(titles)  # Converting to set for easier comparison

            if os.path.exists(file_name):
                with open(file_name, 'r', encoding='utf-8') as file:
                    current_titles = set(file.read().splitlines())
            else:
                current_titles = set()

            # Only update if there are changes
            if titles_set != current_titles:
                with open(file_name, 'w', encoding='utf-8') as file:
                    for title in titles:
                        file.write(f"{title}\n")
                if len(current_titles) == 0:
                    files_created += 1
                    print(f"Created {file_name}")
                else:
                    files_updated += 1
                    print(f"Updated {file_name}")

                added_animes = len(titles_set - current_titles)
                total_animes_added += added_animes

                if added_animes > 0:
                    print(f"Added {added_animes} anime(s) to {file_name}: {', '.join(titles_set - current_titles)}")
        # Print "Everything is up to date" only if no updates were made
        if files_updated == 0 and files_created == 0:
            print("Everything is up to date")
