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
                        return True
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
                    popularity
                    genres
                    siteUrl
                    startDate {
                        year
                    }
                    status
                    format
                    nextAiringEpisode {
                        timeUntilAiring
                        episode
                    }
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
        response = requests.post(
            self.api_url,
            json={'query': query, 'variables': variables},
            headers=self.headers
        )
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
        average_score = anime.get('averageScore')
        popularity = anime.get('popularity', 'N/A')
        genres = ', '.join(anime.get('genres', []))
        site_url = anime['siteUrl']
        watched_status = self.get_watched_status(anime_title)
        media_format = anime.get('format', 'N/A')

        # Determine score to display (average score or popularity)
        if average_score is None:
            score_display = f"Rank #{popularity} (overall popularity)"
        else:
            score_display = f"{average_score}%"

        print(f"{Fore.RED}N{Fore.LIGHTBLACK_EX}ame{Fore.WHITE}: "
              f"{Style.BRIGHT}{Fore.LIGHTWHITE_EX}/"
              f"{Fore.LIGHTCYAN_EX}{anime_title}{Fore.LIGHTWHITE_EX}/"
              f"{Fore.MAGENTA}{year}{Fore.LIGHTWHITE_EX}/"
              f"{Fore.CYAN}{score_display}{Fore.LIGHTWHITE_EX}/")

        next_airing_episode = anime.get('nextAiringEpisode')

        # Adjusted the logic to not set next_airing_episode to None
        if next_airing_episode:
            time_until_airing = next_airing_episode.get('timeUntilAiring', 0)
            episode_number = next_airing_episode.get('episode', 'N/A')
            days = time_until_airing // 86400
            hours = (time_until_airing % 86400) // 3600
            minutes = (time_until_airing % 3600) // 60
            time_str = f"Ep {episode_number}: {days}d {hours}h {minutes}m"
            print(f"{Fore.RED}A{Fore.LIGHTBLACK_EX}iring{Fore.WHITE}: "
                  f"{Style.BRIGHT}{Fore.GREEN}{time_str}")
        else:
            anime_status_raw = anime.get('status', 'N/A')
            anime_status = anime_status_raw.replace('_', ' ').title()
            if anime_status_raw == 'NOT_YET_RELEASED':
                print(f"{Fore.RED}A{Fore.LIGHTBLACK_EX}nime Status{Fore.WHITE}: "
                      f"{Style.BRIGHT}{Fore.RED}Not Yet Released")
            elif media_format.upper() != 'MOVIE':
                print(f"{Fore.RED}A{Fore.LIGHTBLACK_EX}nime Status{Fore.WHITE}: "
                      f"{Fore.GREEN if anime_status.lower() == 'finished' else Fore.RED}{anime_status}")

        # Determine if we should suppress 'Episodes' and 'Status' lines
        suppress_episodes_and_status = False
        if next_airing_episode and (episodes is None or episodes == 'N/A' or episodes == 0) and watched_status == 'Not Seen':
            suppress_episodes_and_status = True

        # Do not display 'Episodes' for movies
        if media_format.upper() == 'MOVIE':
            suppress_episodes_and_status = True

        if not suppress_episodes_and_status:
            print(f"{Fore.RED}E{Fore.LIGHTBLACK_EX}pisodes{Fore.WHITE}: "
                  f"{Style.BRIGHT}{Fore.CYAN}{episodes}")
            print(f"{Fore.RED}S{Fore.LIGHTBLACK_EX}tatus{Fore.WHITE}: "
                  f"{Fore.RED if watched_status == 'Not Seen' else Fore.GREEN}{watched_status}")

        print(f"{Fore.RED}G{Fore.LIGHTBLACK_EX}enres{Fore.WHITE}: "
              f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}{genres}")
        print(f"{Fore.RED}L{Fore.LIGHTBLACK_EX}ink{Fore.WHITE}: "
              f"{Style.BRIGHT}{Fore.LIGHTBLUE_EX}{site_url}")

        if not next_airing_episode:
            recommendations = anime.get('recommendations', {}).get('edges', [])
            unwatched_recommendations = [
                rec['node']['mediaRecommendation']
                for rec in recommendations
                if rec['node']['mediaRecommendation']
                and rec['node']['mediaRecommendation'].get('title')
                and not self.is_watched(rec['node']['mediaRecommendation']['title'].get('romaji', '').lower())
                and (rec['node']['mediaRecommendation'].get('averageScore') or 0) >= 65
            ]

            sorted_recommendations = sorted(
                unwatched_recommendations,
                key=lambda x: x.get('averageScore', 0),
                reverse=True
            )

            if sorted_recommendations:
                print(f"{Fore.RED}R{Fore.LIGHTBLACK_EX}ecommendations{Fore.WHITE}: "
                      f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{len(sorted_recommendations)}")
                for rec in sorted_recommendations:
                    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{rec['title']['romaji']} "
                          f"{Fore.LIGHTWHITE_EX}({Fore.LIGHTMAGENTA_EX}{rec.get('averageScore', 'N/A')}%{Fore.LIGHTWHITE_EX})")
            else:
                print(f"{Fore.RED}Recommendations: None")
