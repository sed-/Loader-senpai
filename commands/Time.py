import requests
import json
class Time:
    requires_api = True
    requires_parameter = True

    def __init__(self, api_url, anime_name=None):
        if not anime_name:
            raise ValueError("Anime name is required for Time.")
        self.api_url = api_url
        self.anime_name = anime_name
        self.headers = self.get_headers()

    @staticmethod
    def get_headers():
        token = Time.get_api_token()
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
        if self.anime_name:
            self.calculate_total_watch_time(self.anime_name)
        else:
            print("Anime name is required for this command.")

    def get_anime_duration(self, anime_name):
        query = """
        query ($search: String) {
          Media(search: $search, type: ANIME) {
            title {
              romaji
            }
            episodes
            duration
            relations {
              edges {
                node {
                  title {
                    romaji
                  }
                  type
                }
                relationType
              }
            }
          }
        }
        """
        variables = {"search": anime_name}
        response = requests.post(self.api_url, json={"query": query, "variables": variables}, headers=self.headers)

        if response.status_code == 200:
            try:
                data = response.json()
                if 'data' in data and 'Media' in data['data']:
                    return data['data']['Media']
                else:
                    print(f"No data available for {anime_name}.")
                    return None
            except json.JSONDecodeError:
                print("Failed to decode JSON from response.")
                return None
        else:
            print(f"Failed to fetch anime data for {anime_name}: {response.status_code}")
            print("Response content:", response.content)
            return None

    def calculate_watch_time(self, anime_data):
        episodes = anime_data.get('episodes', 0)
        duration = anime_data.get('duration', 0)

        if episodes == 0 or duration == 0:
            return 0

        # Subtract 3 minutes per episode for time calculations (1.5 min for opening, 1.5 min for ending)
        adjusted_duration = max(duration - (1.5 + 1.5), 0)
        return episodes * adjusted_duration

    def calculate_total_watch_time(self, anime_name):
        total_minutes_all = 0
        total_minutes_original = 0
        total_episodes_all = 0
        anime_queue = [anime_name]
        processed_anime = set()
        season_counter = 1
        total_seasons = 0

        while anime_queue:
            current_anime = anime_queue.pop(0)
            if current_anime in processed_anime:
                continue

            anime_data = self.get_anime_duration(current_anime)
            if anime_data is None:
                continue

            # Calculate watch time for the current anime
            watch_time = self.calculate_watch_time(anime_data)
            total_minutes_all += watch_time

            # Only calculate and store details for season 1, but do not print
            if season_counter == 1:
                total_minutes_original = watch_time
                total_episodes_original = anime_data.get('episodes', 0)

            total_episodes_all += anime_data.get('episodes', 0)
            season_counter += 1
            total_seasons += 1
            processed_anime.add(current_anime)

            # Check for sequels and add them to the queue
            if 'relations' in anime_data and 'edges' in anime_data['relations']:
                for relation in anime_data['relations']['edges']:
                    if relation['relationType'] == 'SEQUEL' and relation['node']['type'] == 'ANIME':
                        sequel_title = relation['node']['title']['romaji']
                        anime_queue.append(sequel_title)

        # Print total details
        print(f"Total Episodes Season 1: {total_episodes_original}")
        print(f"Total Seasons: {total_seasons}")
        print(f"Total Episodes: {total_episodes_all}")

        # Calculate and print the total watch time for the original anime
        hours_original = int(total_minutes_original // 60)
        minutes_original = int(total_minutes_original % 60)
        print(f"Total time to finish: {hours_original} hours, {minutes_original} minutes.")

        # Calculate and print the total watch time for all seasons
        days_all = int(total_minutes_all // (24 * 60))
        remaining_minutes = int(total_minutes_all % (24 * 60))
        hours_all = int(remaining_minutes // 60)
        minutes_all = int(remaining_minutes % 60)
        print(f"Total time to watch all the seasons: {days_all} days, {hours_all} hours, {minutes_all} minutes")