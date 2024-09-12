import requests
import json

class UserSearchCommand:
    requires_api = True  # Indicates this command needs the API URL
    requires_parameter = True  # Indicates this command requires a parameter

    def __init__(self, api_url, username=None):
        if not username:
            raise ValueError("Username is required for UserSearchCommand.")
        self.api_url = api_url
        self.username = username
        self.headers = self.get_headers()

    @staticmethod
    def get_headers():
        token = UserSearchCommand.get_api_token()
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
            user_data = self.fetch_user_stats(self.username)
            if user_data and 'data' in user_data and 'User' in user_data['data']:
                self._display_stats(user_data['data']['User'])
            else:
                print("No data available for user.")
        else:
            print("Username is required for this command.")

    def fetch_user_stats(self, username):
        """Fetch user statistics using GraphQL query."""
        query = """
        query ($userName: String) {
          User(name: $userName) {
            statistics {
              anime {
                statuses {
                  status
                  count
                }
                meanScore
                episodesWatched
                minutesWatched
                genres { 
                    genre
                    count
                    meanScore
                }
              }
            }
            siteUrl
          }
        }
        """
        variables = {"userName": username}
        response = requests.post(self.api_url, json={"query": query, "variables": variables}, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch user stats for {username}: {response.status_code}")
            try:
                error_details = response.json()
                print("Error details:", json.dumps(error_details, indent=4))
            except json.JSONDecodeError:
                print("Failed to decode JSON from response.")
            return None

    def _display_stats(self, user_data):
        stats = user_data['statistics']['anime']
        total_animes_watched = sum(item['count'] for item in stats.get('statuses', []) if item['status'] == 'COMPLETED')

        print(f"User Profile: {user_data['siteUrl']}")
        print(f"Total Animes Watched: {total_animes_watched}")
        print(f"Total Episodes Watched: {stats['episodesWatched']}")
        print(f"Mean Score: {stats['meanScore']}")
        print(f"Total Time Watched: {self.format_time_watched(stats['minutesWatched'])}")

        print("Genre Overview:")
        for genre in stats['genres']:
            print(f"- {genre['genre']}: Count: {genre['count']}, Mean Score: {genre['meanScore']}")

    def format_time_watched(self, total_minutes):
        years, remainder = divmod(total_minutes, 525600)
        days, remainder = divmod(remainder, 1440)
        hours, minutes = divmod(remainder, 60)
        return f"{years} years, {days} days, {hours} hours, {minutes} minutes" if years > 0 else \
               f"{days} days, {hours} hours, {minutes} minutes" if days > 0 else \
               f"{hours} hours, {minutes} minutes"


