import requests
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class SearchAnime:
    requires_api = True
    requires_parameter = True

    def __init__(self, api_url, anime_title):
        self.api_url = api_url
        self.anime_title = anime_title
        self.headers = self.get_headers()

    @staticmethod
    def get_api_token():
        try:
            with open('token.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Token file not found.")
            return None

    @staticmethod
    def get_headers():
        token = SearchAnime.get_api_token()
        if token:
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        else:
            print("No token available.")
            return {}

    @staticmethod
    def is_anime_in_file(anime_title, filename):
        try:
            anime_title_normalized = anime_title.lower().strip()
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    title_part = line.split(':')[0].strip().lower()
                    if anime_title_normalized == title_part:
                        #print(f"Found match in {filename}: {title_part}")
                        return True
            #print(f"No match found in {filename} for: {anime_title_normalized}")
            return False
        except FileNotFoundError:
            return False

    def get_watched_status(self, anime_title):
        anime_title = anime_title.lower().strip()

        if self.is_anime_in_file(anime_title, 'currently_watching.txt'):
            return "Currently watching"
        elif self.is_anime_in_file(anime_title, 'on_hold.txt'):
            return "On hold"
        elif self.is_anime_in_file(anime_title, 'dropped.txt'):
            return "Dropped"
        elif self.is_anime_in_file(anime_title, 'plan_to_watch.txt'):
            return "Plan to watch"
        elif self.is_anime_in_file(anime_title, 'watched_anime.txt'):
            return "Watched"
        else:
            return "Not Seen"

    def is_watched(self, anime_title):
        return any([
            self.is_anime_in_file(anime_title, 'currently_watching.txt'),
            self.is_anime_in_file(anime_title, 'on_hold.txt'),
            self.is_anime_in_file(anime_title, 'dropped.txt'),
            self.is_anime_in_file(anime_title, 'plan_to_watch.txt'),
            self.is_anime_in_file(anime_title, 'watched_anime.txt')
        ])

    def execute(self):
        self.search_anime()

    def search_anime(self):
        query = """
        query ($name: String) {
            Page {
                media(search: $name, type: ANIME) {
                    id
                    title {
                        romaji
                    }
                    description
                    episodes
                    averageScore
                    genres
                    siteUrl
                    startDate {
                        year
                    }
                    status
                    recommendations {
                        edges {
                            node {
                                mediaRecommendation {
                                    title {
                                        romaji
                                    }
                                    averageScore
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {'name': self.anime_title}
        response = requests.post(self.api_url, json={'query': query, 'variables': variables}, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            media_list = data['data']['Page']['media']
            if media_list:
                self.display_anime_details(media_list[0])
            else:
                print("No results found.")
        else:
            print(f"Error searching for anime: {response.status_code}")
            print(response.text)

    def display_anime_details(self, anime):
        anime_title = anime['title']['romaji']
        episodes = anime.get('episodes', 'N/A')
        year = anime.get('startDate', {}).get('year', 'Unknown')
        average_score = anime.get('averageScore', 'N/A')
        anime_status = anime.get('status', 'N/A').replace('_', ' ').title()
        genres = ', '.join(anime.get('genres', []))
        site_url = anime['siteUrl']
        watched_status = self.get_watched_status(anime_title)

        print(f"{Fore.RED}N{Fore.LIGHTBLACK_EX}ame{Fore.WHITE}: {Style.BRIGHT}{Fore.LIGHTWHITE_EX}/{Fore.LIGHTCYAN_EX}{anime_title}{Fore.LIGHTWHITE_EX}/{Fore.MAGENTA}{year}{Fore.LIGHTWHITE_EX}/{Fore.CYAN}{average_score}%{Fore.LIGHTWHITE_EX}/")
        print(f"{Fore.RED}E{Fore.LIGHTBLACK_EX}pisodes{Fore.WHITE}: {Style.BRIGHT}{Fore.CYAN}{episodes}")
        print(f"{Fore.RED}A{Fore.LIGHTBLACK_EX}nime Status{Fore.WHITE}: {Fore.GREEN if anime_status.lower() == 'finished' else Fore.RED}{anime_status}")
        print(f"{Fore.RED}S{Fore.LIGHTBLACK_EX}tatus{Fore.WHITE}: {Fore.RED if watched_status == 'Not Seen' else Fore.GREEN}{watched_status}")
        print(f"{Fore.RED}G{Fore.LIGHTBLACK_EX}enres{Fore.WHITE}: {Style.BRIGHT}{Fore.LIGHTYELLOW_EX}{genres}")
        print(f"{Fore.RED}L{Fore.LIGHTBLACK_EX}ink{Fore.WHITE}: {Style.BRIGHT}{Fore.LIGHTBLUE_EX}{site_url}")

        recommendations = anime.get('recommendations', {}).get('edges', [])
        unwatched_recommendations = [
            rec['node']['mediaRecommendation'] for rec in recommendations
            if rec['node']['mediaRecommendation'] and rec['node']['mediaRecommendation'].get('title')
            and not self.is_watched(rec['node']['mediaRecommendation']['title'].get('romaji', '').lower())
            and (rec['node']['mediaRecommendation'].get('averageScore') or 0) >= 65
        ]

        sorted_recommendations = sorted(unwatched_recommendations, key=lambda x: x.get('averageScore', 0), reverse=True)

        if sorted_recommendations:
            print(f"{Fore.RED}R{Fore.LIGHTBLACK_EX}ecommendations{Fore.WHITE}: {Fore.LIGHTCYAN_EX}{Style.BRIGHT}{len(sorted_recommendations)}")
            for rec in sorted_recommendations:
                print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{rec['title']['romaji']} {Fore.LIGHTWHITE_EX}({Fore.LIGHTMAGENTA_EX}{rec.get('averageScore', 'N/A')}%{Fore.LIGHTWHITE_EX})")
        else:
            print(f"{Fore.RED}Recommendations: None")
