import os
import requests
import time
import webbrowser

class AniListAuth:
    requires_api = False

    def __init__(self):
        # Prompt the user to enter client ID and secret
        self.client_id = input("Please enter your client ID: ")
        self.client_secret = input("Please enter your client secret: ")
        self.redirect_uri = 'https://anilist.co/api/v2/oauth/pin'
        self.access_token = None

    def get_authorization_code(self):
        # Construct the authorization URL
        auth_url = f"https://anilist.co/api/v2/oauth/authorize?client_id={self.client_id}&redirect_uri={self.redirect_uri}&response_type=code"
        
        # Open the authorization URL in the user's web browser
        webbrowser.open(auth_url)
        
        # Prompt the user for the authorization code
        return input("Please enter the authorization code: ")

    def request_access_token(self, code):
        # Token URL
        token_url = 'https://anilist.co/api/v2/oauth/token'
        
        # Payload for the POST request
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        try:
            # Send POST request to get access token
            response = requests.post(token_url, data=data)
            response.raise_for_status()  # Raise exception for HTTP errors

            # Extract access token from response
            self.access_token = response.json().get('access_token')
            if not self.access_token:
                raise KeyError("Access token not found in response.")
            
            # Save the access token to a file
            self.save_token()

        except (requests.RequestException, KeyError) as e:
            print(f"Error retrieving access token: {e}")

    def save_token(self):
        # Save the access token to a file
        with open("token.txt", "w") as token_file:
            token_file.write(self.access_token)

        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')

        # Notify user of successful token storage
        print("Token saved successfully!")
        time.sleep(1)

    def execute(self):
        # Get authorization code and request the access token
        code = self.get_authorization_code()
        self.request_access_token(code)
