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
