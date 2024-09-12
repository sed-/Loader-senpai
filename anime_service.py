import requests
import json

class AnimeService:
    def __init__(self, api_url, headers):
        self.api_url = api_url
        self.headers = headers

    @staticmethod
    def get_api_token():
        """Static method to retrieve the API token from a file."""
        try:
            with open('token.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Token file not found.")
            return None

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
