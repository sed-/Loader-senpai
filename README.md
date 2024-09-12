# Loader-senpai
---

### Steps to Set Up AniList Integration

#### 1. Get Your Client ID and Client Secret
   - **Log in to AniList**: Visit the [AniList developer page](https://anilist.co/settings/developer) and sign in.
   - **Create a New App**: Look for a "Create New Client" button after logging in.
   - Fill out the app Name (This can be w/e you want)
   - For the Redirect URL, enter the following URL: `https://anilist.co/api/v2/oauth/pin`.
   - **Save the Client ID and Secret**: Once the app is created, copy your Client ID and Client Secret somewhere safe.

#### 2. **Run the Token Process**
   - Run the script `1.Loader-Senpai.py`.
   - When prompted, type your AniList username, after type `token`. This will initiate the token authentication process.

#### 3. **Set the Username (Optional)**
   - If the script doesn’t ask for your username during setup, manually open the file `username.txt` and enter your AniList username there.

#### 4. **Completion**
   - Once the setup is complete, type `features` to see the list of available features and how to use them.

--- 
