from os import getenv
from dotenv import load_dotenv

from random import choice

from utils.helpers import load_yaml

class Settings:
    def __init__(self) -> None:
        # Load the environment file.
        load_dotenv(verbose=True)

        # Load the needed files.
        self.general = load_yaml("settings.yml")
        self.subreddits = load_yaml("subreddits.yml")

        if self.general == None or self.subreddits == None:
            print("Failed to load the settings or subreddits.")
            exit()

    def get_random_subreddit(self, exclude: list = []):
        subreddit = choice(self.subreddits)
        return subreddit if subreddit not in exclude else self.get_random_subreddit(exclude)

    @property
    def reddit_auth_info(self) -> dict:
        return {
            "client_id": getenv("REDDIT_CLIENT_ID"),
            "client_secret": getenv("REDDIT_CLIENT_SECRET"),
            "refresh_token": getenv("REDDIT_REFRESH_TOKEN"),
        }

    @property
    def submissions_webhook(self) -> str:
        return getenv("DISCORD_SUBMISSIONS_WEBHOOK")
