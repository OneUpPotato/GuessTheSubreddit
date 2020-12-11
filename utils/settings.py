"""
Copyright (c) 2020 OneUpPotato

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
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

        if self.general is None or self.subreddits is None:
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

    @property
    def sentry_url(self) -> str:
        return getenv("SENTRY_URL")
