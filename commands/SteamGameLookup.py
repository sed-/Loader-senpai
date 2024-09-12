# File: SteamGameLookup.py

import requests
from lxml import html
import urllib.parse
import re

class SteamGameLookup:
    requires_api = False
    requires_parameter = True
    requires_username = False

    def __init__(self, parameter=None, api_url=None):
        self.parameter = parameter
        self.api_url = api_url
        self.session = requests.Session()
        self.session.cookies.set('birthtime', '568022401')
        self.session.cookies.set('lastagecheckage', '1-January-1970')

    def execute(self):
        if not self.parameter:
            print("No game title provided.")
            return

        game_title = self.parameter
        game_id, error = self.get_game_id(game_title)
        if error:
            print(error)
        else:
            game_info = self.scrape_steam_page(game_id)
            print(game_info)

    def extract_rating_percentage(self, text):
        match = re.search(r'(\d+%)', text)
        return match.group(1) if match else "Rating not found"

    def get_game_id(self, game_title):
        url = f"https://store.steampowered.com/search/?term={urllib.parse.quote_plus(game_title)}"
        response = self.session.get(url)
        if response.status_code != 200:
            return None, "Failed to connect to Steam."
        game_ids = html.fromstring(response.content).xpath('//a[@data-ds-appid]/@data-ds-appid')
        return (game_ids[0], None) if game_ids else (None, "No game found.")

    def scrape_steam_page(self, game_id):
        details = self.fetch_game_details(game_id)
        player_stats = self.fetch_player_stats(game_id)
        return self.format_game_info(details, player_stats)

    def fetch_game_details(self, game_id):
        url = f"https://store.steampowered.com/app/{game_id}/"
        response = self.session.get(url, allow_redirects=True)
        if "agecheck" in response.url:
            url = response.url.replace('agecheck', 'app')
        response = self.session.get(url)
        if response.status_code != 200:
            return "Failed to access game page on Steam."
        page = html.fromstring(response.content)
        details = {
            "title": self.get_xpath_text(page, '//div[@class="apphub_AppName"]/text()'),
            "recent_reviews": self.extract_rating_percentage(self.get_xpath_text(page, '(//div[contains(@class,"user_reviews_summary_row")])[1]/@data-tooltip-html')),
            "overall_rating": self.extract_rating_percentage(self.get_xpath_text(page, '(//div[contains(@class,"user_reviews_summary_row")])[2]/@data-tooltip-html')),
            "release_date": self.get_xpath_text(page, '//div[@class="release_date"]/div[2]/text()'),
            "price": self.get_xpath_text(page, '//div[contains(@class,"game_purchase_price") or contains(@class,"discount_original_price")]/text()'),
            "genre": ', '.join([genre.strip() for genre in page.xpath('//div[contains(@class,"glance_tags")]/a[contains(@class,"app_tag")]/text()')[:4]])
        }
        return details

    def get_xpath_text(self, page, xpath_query):
        try:
            return page.xpath(xpath_query)[0].strip()
        except IndexError:
            return "Not found"

    def fetch_player_stats(self, game_id):
        url = f"https://steamcharts.com/app/{game_id}"
        response = self.session.get(url)
        if response.status_code != 200:
            return {"hour": "Data not available", "day": "Data not available"}

        tree = html.fromstring(response.content)
        player_stats = {
            "hour": self.get_player_count(tree, '/html/body/div[3]/div[3]/div[1]/span/text()'),
            "day": self.get_player_count(tree, '/html/body/div[3]/div[3]/div[2]/span/text()')
        }
        return player_stats

    def get_player_count(self, tree, xpath):
        try:
            player_count = tree.xpath(xpath)[0].strip()
            return "{:,}".format(int(player_count))
        except (IndexError, ValueError):
            return "Data not available"

    def format_game_info(self, details, player_stats):
        return (f"{details['title']} ({details['release_date']})\nGenre: {details['genre']}\n"
                f"Overall Rating: {details['overall_rating']}\nRecent Rating: {details['recent_reviews']}\n"
                f"Playercount 1hour: {player_stats['hour']}\nPlayercount 24hours: {player_stats['day']}\nCost: {details['price']}")

    def command_factory(self, user_input):
        commands = {
            'quit': self.quit,
            'lookup': self.lookup_game_details
        }
        command = user_input.split()[0].lower()
        return commands.get(command, self.unknown_command)

    def quit(self):
        print("Exiting Steam-assistant.")
        exit()

    def lookup_game_details(self, game_title):
        game_id, error = self.get_game_id(game_title)
        if error:
            print(error)
        else:
            game_info = self.scrape_steam_page(game_id)
            print(game_info)

    def unknown_command(self):
        print("Unknown command. Please use 'lookup [game title]' to find game details.")

    def run(self):
        while True:
            user_input = input("Steam-assistant: What do you want to do? ").strip()
            action = self.command_factory(user_input)
            action(user_input)

if __name__ == "__main__":
    lookup = SteamGameLookup()
    lookup.run()
