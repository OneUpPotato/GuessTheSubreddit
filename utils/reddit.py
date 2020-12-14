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
from praw import Reddit
from praw.models import Subreddit

from utils.settings import Settings


class GTSReddit(Reddit):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        super().__init__(**self.settings.reddit_auth_info, user_agent="GuessTheSubreddit Bot v2.1 (by u/OneUpPotato)")
        print(f"Logged in as u/{self.user.me().name}")

    @property
    def main_subreddit(self) -> Subreddit:
        return self.subreddit(self.settings.general["subreddit"])
