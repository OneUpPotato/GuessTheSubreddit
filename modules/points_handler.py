from sortedcollections import ValueSortedDict

from num2words import num2words

from textwrap import dedent

class PointsHandler:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.flair_settings = self.bot.settings.general["flairs"]

        # Load all of the scores.
        self.load_scores()

    def load_scores(self) -> None:
        """
        Loads all of the scores from the flairs on Reddit.
        """
        self.scores = ValueSortedDict({})
        for flair in self.bot.reddit.main_subreddit.flair(limit=None):
            try:
                self.scores[flair["user"].name.lower()] = int(
                    "".join([char for char in flair["flair_text"].split(" ")[0] if char.isnumeric()])
                )
            except Exception as e:
                print(e)
                pass
        print("POINTS: Loaded scores.")

    def update_score(self, username: str, amount: int) -> None:
        """
        Updates the score of a user.
        :param username: The user whose score is being updated.
        :param amount: The amount to modify their score by.
        """
        username = username.lower()

        # Check if the user has a score already.
        if username not in self.scores.keys():
            self.scores[username] = amount
            self.bot.reddit.main_subreddit.flair.set(
                username,
                self.flair_settings["user"]["score"]["text"].format(amount),
                flair_template_id=self.flair_settings["user"]["score"]["id"],
            )
        else:
            self.scores[username] += amount
            self.bot.reddit.main_subreddit.flair.set(
                username,
                self.flair_settings["user"]["score"]["text"].format(self.scores[username]),
            )

    def generate_leaderboard_table(self):
        """
        Generates a leaderboard table. This is used for the widget and sidebar.
        """
        leaderboard_table = dedent("""
            |**Place**|**Username**|**Points**|
            |:-:|:-:|:-:|
        """).strip()

        # For the top 10 users.
        for i, score_info in enumerate(reversed(self.scores.items()[-10:])):
            leaderboard_table += f"\n|{num2words((i + 1), to='ordinal_num')}|{score_info[0]}|{score_info[1]}|"

        return leaderboard_table
