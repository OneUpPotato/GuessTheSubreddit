import sentry_sdk

from utils.reddit import GTSReddit
from utils.settings import Settings

from modules.points_handler import PointsHandler
from modules.post_handler import PostsHandler
from modules.schedular import Schedular
from modules.widgets import Widgets

class GuessTheSubreddit:
    def __init__(self):
        # Load the configurations.
        self.settings = Settings()

        # Initiate the Reddit instance.
        self.reddit = GTSReddit(settings=self.settings)

        # Initiate Sentry (if a URL is provided in the ENV file)
        self.sentry = None
        if self.settings.sentry_url:
            self.sentry = sentry_sdk
            self.sentry.init(self.settings.sentry_url)

        # Initiate sections of the bot.
        self.points = PointsHandler(bot=self)
        self.widgets = Widgets(bot=self)
        self.posts = PostsHandler(bot=self)
        self.schedular = Schedular(bot=self)

        # Update the widgets.
        self.widgets.update()
