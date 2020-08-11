from os import getenv
from dotenv import load_dotenv

settings = {}
subreddits_list = []

# Load the .env file.
load_dotenv(verbose=True)

# Get the required Reddit login info.
def get_reddit_login_info():
    return {
        "client_id": getenv("REDDIT_CLIENT_ID"),
        "client_secret": getenv("REDDIT_CLIENT_SECRET"),
        "refresh_token": getenv("REDDIT_REFRESH_TOKEN"),
    }

from helpers import load_jsoc
from post_handler import load_wiki
from points_handler import load_scores

# Load all the configuration files.
# This is the first thing called in main.py
def load_configs():
    global settings, subreddits_list

    # Load the settings.yml and subreddits.yml files.
    settings = load_jsoc("settings.yml")
    subreddits_list = [subreddit.lower() for subreddit in load_jsoc("subreddits.yml")["subreddits"]]

    # This is here until a fix can be found for the problem decoding unicode from settings files.
    settings["flairs"]["user"]["score"]["text"] = "△{}"

    # Load the wiki pages for post handler.
    load_wiki()

    # Load the scores using the subreddit flairs.
    load_scores()

    # Print a message saying that the configs have succesfully been loaded.
    print("Succesfully loaded the configuration files.")

# Get the list of subreddits.
def get_subreddits_list():
    return subreddits_list

# Get the settings loaded from the file.
def get_settings():
    return settings

# Get the subreddit name from the settings dict.
def get_subreddit_name():
    return settings["subreddit_name"]

# Get the flairs from the settings dict
def get_flairs():
    return settings["flairs"]

# Get the discord webhook URL to post new submissions.
def get_submissions_webhook():
    return getenv("DISCORD_SUBMISSIONS_WEBHOOK")

# Get the Sentry URL from the env file.
def get_sentry_url():
    return getenv("SENTRY_URL")
