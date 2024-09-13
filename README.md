---

##🌟 **Welcome to Loader-Senpai’s ReadMe!** 🌟
Ready to level up your anime experience? Loader-Senpai is here to help you manage, track, and explore your anime lists with ease. Let’s dive into some of the awesome features!

##🔥 **Key Features** 🔥

✨ **Personalized Suggestions**
Say goodbye to repeat recommendations! Loader-Senpai syncs with your profile to suggest only fresh anime picks—no more seeing shows you’ve already watched.

📋 **Effortless List Management**
Keep all your anime lists (completed, on-hold, dropped, etc.) in one place. No need to juggle different apps—everything’s right here!

👥 **Compare with Friends**
Ever wonder how your watchlist stacks up against your friends’? Compare lists to see what anime you’re missing out on, or find new recommendations to watch together.

📊 **Anime Stats—Yours & Theirs**
Track your own anime stats or check out your friends’ progress.

🎮 **Steam Games Explorer**
Also into gaming? You can search up steam games and see there current player count.

🔒 **Backup Your Lists**
No more worries about losing track of your anime! Loader-Senpai can back up your lists, so you always have a safe copy.

⚡ **And So Much More!**
These are just a few of the ways Loader-Senpai can make your anime and gaming adventures even better. Dive in and explore all it has to offer!

---

---

## 🌸 **Welcome to the Loader-Senpai AniList Integration Setup!** 🌸

Whether you're a casual anime enthusiast or a seasoned otaku, Loader-Senpai is here to make your AniList experience seamless. Follow these simple steps, and you’ll be ready to manage your anime lists like a true senpai. However, please note that this is an **unstable build**, recommended for more experienced users. Proceed with caution, and feel free to unleash your creativity! 🎨

---

### ⚔️ **Step 1: Obtain Your AniList API Credentials**

To access the vast world of AniList, you’ll need to arm yourself with your own **Client ID** and **Client Secret**. Think of this as your personal summoning scroll to the AniList API!

1. **Head to AniList**: Visit the [AniList Developer Page](https://anilist.co/settings/developer) and sign in with your credentials.
   
2. **Create Your App**: Hit the "Create New Client" button, then fill out the required fields, like your app’s name and a short description. This is your app’s backstory!

3. **Set the Redirect URL**: For this, enter the URL: `https://anilist.co/api/v2/oauth/pin`. This will let you gain access to your AniList profile via Loader-Senpai’s script. ⚙️

4. **Save Your Credentials**: Once your app is created, AniList will give you your **Client ID** and **Client Secret**. Jot these down in a safe place. You’ll need them soon!

---

### 🛠️ **Step 2: Initiate Token Authentication**

Now that you have your API credentials, it’s time to make a pact with AniList. This is the key to accessing your anime and manga lists!

- **Run the Script**: Fire up `1.Loader-Senpai.py` to begin. 💻
  
- **Enter Your Username**: When prompted, input your **AniList username**. Afterward, type `token` to trigger the authentication process.

Loader-Senpai will guide you through obtaining your access token. This will allow the program to interact with your AniList data.

---

### ⚡ **Step 3: Install Dependencies**

Before proceeding, make sure you have all the necessary components installed. 🛠️ Loader-Senpai’s abilities rely on a few magical tools in the form of Python libraries.

Run the following command in your terminal to install everything needed:

```bash
pip install -r requirements.txt
```



### 🧠 **Step 4: Customize and Add New Features (Advanced)**

Loader-Senpai comes with a flexible structure, but be aware—this feature is for **advanced users** only. It's unstable and requires a good understanding of Python. If you want to experiment and add your own commands, here's how:

#### **Main Files**:
- `loader.py` (Base loader for the program)
- `command_factory.py` (The main brain 🧠)
- `anime_service.py` (The anime brain, handling AniList tasks)
- `commands.json` (Where commands/features are added, modified, or deleted)

#### **How to Add a New Feature**:
1. **Create Your Feature Class**: Your custom feature must follow this structure:
   ```python
   class FeatureName:
       requires_api = False
       requires_parameter = False
       requires_username = False
   ```
   By default, any unmarked values (i.e., not set to `False`) will be assumed to be `True`. So, make sure to set them according to your feature’s needs to avoid API errors. 

2. **Add Your Feature**:
   - Drop your `.py` file in the same folder as the other scripts.
   - Open `commands.json` and add the new feature there.
   - Update `features.txt` to include a description of the new feature.
   
3. **Win!** 🏆

Remember, this setup is still in development, so some commands may not behave as expected if misconfigured.

---

### 🎌 **Step 5: You’re Ready to Roll!**

Congratulations, fellow senpai! You’ve completed the setup. Now you can explore all the features Loader-Senpai has to offer. Ready to see what tricks are up its sleeve? Type `features` to get a full list of commands!

**Here are some of the cool features**:

- **Track Your Anime**: Keep tabs on your current anime progress with ease!
- **Top Anime Recommendations**: Want to discover new shows? Loader-Senpai can recommend some based on your watch history.
- **Anime and Manga Search**: Look up titles from AniList’s massive database. 📚

And much more...

---

### 🎥 **Bonus: Anime Hype Up**

To keep the anime spirit high, make sure you always keep a playlist of your favorite anime OPs and EDs running in the background as you dive into your list! 🎶 Nothing boosts productivity more than some hype tunes from **Attack on Titan** or the calming tracks of **Your Lie in April**.

---
