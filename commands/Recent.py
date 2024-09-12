import requests
import json

class Recent:
    requires_api = True         # Indicates this command needs the API URL
    requires_parameter = False  # Indicates this command does not necessarily require a parameter

    def __init__(self, api_url, watched_anime_file='watched_anime.txt'):
        self.api_url = api_url
        self.watched_anime = self.load_watched_anime(watched_anime_file)
        self.headers = self.get_headers()

    @staticmethod
    def get_headers():
        token = Recent.get_api_token()
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

    def load_watched_anime(self, filename):
        try:
            with open(filename, 'r') as file:
                return {line.strip() for line in file}
        except FileNotFoundError:
            print(f"Warning: {filename} not found. No anime will be filtered out as watched.")
            return set()

    def fetch_recent_anime(self):
        query = '''
        query {
            Page(page: 1, perPage: 50) {
                media(type: ANIME, status: FINISHED, sort: END_DATE_DESC) {
                    title {
                        romaji
                    }
                    siteUrl
                    averageScore
                    stats {
                        scoreDistribution {
                            score
                            amount
                        }
                    }
                }
            }
        }
        '''
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return data['data']['Page']['media']
        else:
            print(f"Error fetching recently finished anime: {response.status_code}")
            return None

    def display_recent_anime(self):
        recent_anime = self.fetch_recent_anime()
        if recent_anime:
            enhanced_anime_list = []
            for anime in recent_anime:
                title = anime['title']['romaji']
                url = anime['siteUrl']
                score = anime['averageScore']
                if score is None and 'stats' in anime and anime['stats']['scoreDistribution']:
                    score = self.calculate_mean_score(anime['stats']['scoreDistribution'])
                if score is None:
                    score = 0  # Ensures all items can be sorted even if no score is provided
                enhanced_anime_list.append((title, score, url))

            # Filter by score and watched status
            filtered_anime_list = [
                anime for anime in enhanced_anime_list
                if anime[1] >= 65 and anime[0] not in self.watched_anime
            ]

            # Sort by score in descending order
            sorted_anime_list = sorted(filtered_anime_list, key=lambda x: x[1], reverse=True)

            print("Some animes to catch up on:")
            for idx, (title, score, url) in enumerate(sorted_anime_list, start=1):
                score_display = f"{int(score)}%" if score > 0 else "N/A"
                print(f"{idx}. {title} ({score_display})")

            self.get_user_choice(sorted_anime_list)

    def get_user_choice(self, anime_list):
        while True:
            user_input = input("Enter the number of the anime to get the link or 'n' to stop: ").strip().lower()
            if user_input in ['n', 'no']:
                break
            try:
                choice = int(user_input)
                selected_anime = next((anime for idx, anime in enumerate(anime_list, start=1) if idx == choice), None)
                if selected_anime:
                    print(f"The link for {selected_anime[0]} is: {selected_anime[2]}")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number or 'n' to stop.")

    def calculate_mean_score(self, score_distribution):
        total_score = 0
        total_count = 0
        for entry in score_distribution:
            total_score += entry['score'] * entry['amount']
            total_count += entry['amount']
        return total_score / total_count if total_count > 0 else None

    def execute(self):
        self.display_recent_anime()


