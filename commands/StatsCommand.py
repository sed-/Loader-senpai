# statscommand.py
import requests
import json

class StatsCommand:
    requires_api = True  # Indicates this command needs the API URL
    requires_parameter = False  # Indicates this command does not require a parameter
    requires_username = True  # Indicates this command requires a username

    def __init__(self, api_url, username=None):
        if not username:
            username = self.get_username_from_file()
            if not username:
                raise ValueError("Username is required for StatsCommand.")
        self.api_url = api_url
        self.username = username
        self.headers = self.get_headers()

    @staticmethod
    def get_username_from_file():
        try:
            with open('username.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Username file not found.")
            return None

    @staticmethod
    def get_headers():
        token = StatsCommand.get_api_token()
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

    def fetch_user_stats(self):
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
        variables = {"userName": self.username}
        response = requests.post(self.api_url, json={"query": query, "variables": variables}, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch user stats for {self.username}: {response.status_code}")
            try:
                error_details = response.json()
                print("Error details:", json.dumps(error_details, indent=4))
            except json.JSONDecodeError:
                print("Failed to decode JSON from response.")
            return None

    def execute(self):
        user_data = self.fetch_user_stats()
        if user_data and 'data' in user_data and 'User' in user_data['data']:
            self._display_stats(user_data['data']['User'])
        else:
            print("No data available for user.")

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
        # This method formats the total minutes watched into years, days, hours, and minutes
        years, remainder = divmod(total_minutes, 525600)
        days, remainder = divmod(remainder, 1440)
        hours, minutes = divmod(remainder, 60)
        if years > 0:
            return f"{years} years, {days} days, {hours} hours, {minutes} minutes"
        elif days > 0:
            return f"{days} days, {hours} hours, {minutes} minutes"
        else:
            return f"{hours} hours, {minutes} minutes"

if __name__ == "__main__":
    api_url = "https://graphql.anilist.co"
    stats_command = StatsCommand(api_url)
    stats_command.execute()
