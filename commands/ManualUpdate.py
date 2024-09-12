import requests

class ManualUpdate:
    requires_api = True  # Indicates this command needs the API URL
    requires_parameter = False  # Indicates this command does not require a parameter
    requires_username = True  # Indicates this command requires a username

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
        """Read the username from a file."""
        try:
            with open('username.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Username file not found.")
            return None

    @staticmethod
    def get_api_token():
        """Read the API token from a file."""
        try:
            with open('token.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Token file not found.")
            return None

    def get_headers(self):
        """Construct headers for the HTTP request."""
        token = self.get_api_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def load_existing_titles(self):
        """Load existing anime titles from file for comparison."""
        try:
            with open('watched_anime.txt', 'r', encoding='utf-8') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            print("Completed titles file not found.")
            return set()

    def execute(self):
        """Execute the update process by querying the API and updating the list."""
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
        """Process the API response and update the title list."""
        if 'data' in json_response:
            new_titles = []
            lists = json_response['data']['MediaListCollection']['lists']
            for list in lists:
                for entry in list['entries']:
                    if entry['status'] == 'COMPLETED':
                        title = entry['media']['title']['romaji']
                        if title not in self.existing_titles:
                            new_titles.append(title)

            self.update_titles(new_titles)
        else:
            print("No useful data in response.")

    def update_titles(self, new_titles):
        """Update the watched_anime.txt file with new titles."""
        if new_titles:
            with open('watched_anime.txt', 'a', encoding='utf-8') as file:
                added_animes = 0
                for title in new_titles:
                    file.write(f"{title}\n")
                    added_animes += 1
            print(f"Added {added_animes} new animes. Check 'watched_anime.txt' for the updated list.")
        else:
            print("No new animes to add.")


