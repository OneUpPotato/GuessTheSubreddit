from praw.models import Submission, MoreComments

from textwrap import dedent

from re import sub
from json import loads, dumps
from random import randint, choice, sample, shuffle

from time import sleep
from datetime import timedelta

from utils.helpers import format_title, get_current_utc, get_utc_timestamp, post_webhook, format_time

class PostsHandler:
    def __init__(self, bot) -> None:
        self.bot = bot

        self.post_types = [
            "standard", # Standard
            "multi", # Multiple Choice
            "fillblank", # Fill the blank.
            "jumbled", # Obfuscation
        ]

        # Load all of the active post info required.
        self.load_info()

    def load_info(self) -> None:
        """
        Loads info on all the active posts and some previous posts.
        """
        # Information on all currently open posts.
        self.pid_to_info = {}

        # Active guessing posts to the expiry timestamp.
        self.pid_to_expiry = {}

        # Post IDs of submissions already posted before.
        # Submissions with these ids are ignored when getting a random submission.
        self.ignore_posts = []

        # Load the info from the wiki pages.
        self.pid_to_info = loads(self.bot.reddit.main_subreddit.wiki["pidtoinfo"].content_md)
        self.pid_to_expiry = loads(self.bot.reddit.main_subreddit.wiki["pidtoexpiry"].content_md)
        self.ignore_posts = loads(self.bot.reddit.main_subreddit.wiki["ignoreposts"].content_md)[:100]

        print("Loaded post info.")

    def update_info(self) -> None:
        """
        Updates the info wiki pages with the post id to info and expiry, and the posts to ignore.
        """
        self.bot.reddit.main_subreddit.wiki["pidtoinfo"].edit(dumps(self.pid_to_info), reason="Updated list due to new post/post closure.")
        self.bot.reddit.main_subreddit.wiki["pidtoexpiry"].edit(dumps(self.pid_to_expiry), reason="Updated list due to new post/post closure.")
        self.bot.reddit.main_subreddit.wiki["ignoreposts"].edit(dumps(self.ignore_posts), reason="Updated list due to new post/post closure.")

    def get_random_submission(self) -> Submission:
        search = {
            "subreddit": self.bot.settings.get_random_subreddit(),
            "exclusions": [],
            "found": False,
        }

        # Search for a post on a random subreddit.
        while search["found"] == False:
            submissions = []
            for submission in self.bot.reddit.subreddit(search["subreddit"]).top("day", limit=25):
                if submission.domain.lower() == "i.redd.it":
                    submissions.append(submission)

            # If there are not enough posts, then try a different subreddit.
            if len(submissions) >= 1:
                # We've found a viable subreddit.
                search["found"] = True

                # Check that the submission hasn't already been used.
                submission = choice(submissions)
                if submission.id not in self.ignore_posts:
                    return submission

            # Try a different subreddit.
            search["exclusions"].append(search["subreddit"])
            search["subreddit"] = self.bot.settings.get_random_subreddit(search["exclusions"])

    def store_info(self, post_id: str, info: dict) -> None:
        """
        Store the information on a new GuessTheSubreddit post.
        :param info: The post info to store.
        """
        self.pid_to_info[post_id] = info
        self.pid_to_expiry[post_id] = get_utc_timestamp() + (self.bot.settings.general["post_expiry_time"] * 60)
        self.ignore_posts.append(info["org_pid"])

        # Save the new additions.
        self.update_info()

    def comment_text(self, type: str, subreddit: str) -> str:
        """
        Generate some comment text for a new post.
        :param type: The type of post (and hint to give).
        :param subreddit: The correct subreddit answer.
        :return: The hint comment text.
        """
        type_settings = self.bot.settings.general["types"][type]
        type_text = type_settings["type_text"]
        if type == "fillblank":
            # Give how many characters are in the subreddit name.
            text = f"r/{'_' * len(subreddit)} ({len(subreddit)} characters)"

            type_text = type_text.format(text)
        elif type == "jumbled":
            # Shuffle the characters in the subreddit name.
            chars = list(subreddit.split(""))
            shuffle(chars)
            text = "r/" + "".join(chars)

            type_text = type_text.format(text)
        elif type == "multi":
            # Get three other random subreddits to show in the list.
            list = sample([sub for sub in self.bot.settings.subreddits if sub != subreddit], 3) + [subreddit]

            # Check if the subreddit has a group subreddit.
            grouped_sub = None
            for grouping in type_settings["groupings"]:
                if subreddit in grouping:
                    grouped_sub = subreddit
                    break

            if grouped_sub != None:
                # There is a chance of using the group subreddit.
                if randint(0, 1) == 1:
                    del list[0]
                    list.append(grouped_sub)

            # Shuffle the list.
            shuffle(list)

            type_text = type_text.format(*list)

        # Wrap the type_text in section seperators.
        seperator = "\n\n&#x200B;\n\n"
        if type_text != "":
            type_text = f"{seperator}{type_text}{seperator}"

        # Get the closing time.
        closing_time = (get_current_utc() + timedelta(minutes=self.bot.settings.general["post_expiry_time"])).strftime("%d/%m/%Y at %H:%M")
        closure_info = self.bot.settings.general["templates"]["comments"]["post"]["closure_info"]["default"].format(closing_time=closing_time)

        # Format the gathered info into the main comment template.
        return self.bot.settings.general["templates"]["comments"]["post"]["main"].format(
            header=self.bot.settings.general["templates"]["comments"]["post"]["headers"]["default"],
            closure_info=closure_info,
            type_text=type_text,
        )

    def comment_text_complete(self, current: str, post_info: dict) -> str:
        """
        Modify some comment text for a post that has been closed.
        :param current: The current comment text.
        :param post_info: Information on the original post.
        :return: The closed post comment text.
        """
        # Get the currently used type text.
        type_text_sep_start = "[](#type_text)"
        type_text_sep_end = "[](#type_text_end)"
        type_text = current[current.find(type_text_sep_start) + len(type_text_sep_start): current.find(type_text_sep_end)]

        # Get some information from the post.
        original_post = self.bot.reddit.submission(post_info["org_pid"])
        permalink = f"https://redd.it/{post_info['org_pid']}"
        try:
            permalink = original_post.permalink
            post_info["org_auth"] = original_post.author.name
        except:
            post_info["org_auth"] = "[deleted]"
            pass

        # Format the closed post info (shows where a post originally came from)
        closure_info = self.bot.settings.general["templates"]["comments"]["post"]["closure_info"]["complete"].format(
            subreddit=post_info["org_sub"],
            author=post_info["org_auth"],
            permalink=permalink,
        )

        # Add a section seperator to the closure info.
        seperator = "\n\n"
        closure_info = seperator + closure_info + seperator

        # Format the gathered info into the main comment template.
        return self.bot.settings.general["templates"]["comments"]["post"]["main"].format(
            header=self.bot.settings.general["templates"]["comments"]["post"]["headers"]["complete"],
            closure_info=closure_info,
            type_text=type_text,
        )


    def submit_post(self, type: str = None) -> None:
        """
        Submits a new guess the subreddit post.
        :param type: The type of post to submit.
        """
        print("POSTS: Posting a new submission.")

        if type == None:
            type = choice(self.post_types)

        # Get a random submission.
        submission = self.get_random_submission()

        # Make a post on the subreddit.
        subreddit_submission = self.bot.reddit.main_subreddit.submit(
            title=format_title(submission.title),
            url=submission.url,
            nsfw=submission.over_18,
            spoiler=submission.spoiler,
        )

        # Set the post flair.
        subreddit_submission.flair.select(self.bot.settings.general["flairs"]["post"][type])

        # Reply with the hint comment.
        comment = None
        sleep(5)
        try:
            comment = subreddit_submission.reply(
                self.comment_text(
                    type,
                    submission.subreddit.display_name.lower(),
                )
            )

            # Distinguish and lock the main comment.
            comment.mod.distinguish(how="yes", sticky=True)
            comment.mod.lock()
        except Exception as e:
            self.bot.sentry.capture_exception(e)
            pass
        sleep(5)

        # Store the post information.
        self.store_info(
            post_id=subreddit_submission.id,
            info={
                "type": type,
                "comment_id": comment.id,
                "org_pid": submission.id,
                "org_sub": submission.subreddit.display_name.lower(),
                "org_auth": submission.author.name,
            },
        )

        # Send a message to the submissions feed.
        post_webhook(
            self.bot.settings.submissions_webhook,
            {
                "title": subreddit_submission.title,
                "description": choice(
                    [
                        "There's a new post to guess on!",
                        "A new post has been added! :)",
                        "Guessing time! There's a new post.",
                    ]
                ),
                "url": f"https://reddit.com{subreddit_submission.permalink}",
                "image": {"url": subreddit_submission.url},
                "timestamp": format_time(subreddit_submission.created_utc),
            },
        )

        print("POSTS: Succesfully posted a new submission.")

    def close_post(self, post_id: str) -> None:
        """
        Handles closing posts. This is called when they reach their closing time.
        :param post_id: The id of the post to close.
        """
        post_info = self.pid_to_info[post_id]

        # Lock the post.
        post = self.bot.reddit.submission(post_id)
        post.mod.lock()

        # Edit the primary comment.
        comment = self.bot.reddit.comment(post_info["comment_id"])
        comment.edit(self.comment_text_complete(comment.body, post_info))

        # Get the amount of points to award on correct comments.
        points = self.bot.settings.general["types"][post_info["type"]]["points_awarded"]

        # Prepare some things before awarding.
        already_awarded = {}
        reply_templates = self.bot.settings.general["templates"]["comments"]["reply"]
        correct_subreddit = sub("^[^a-zA-Z0-9]*|[^a-zA-Z0-9]", "", post_info["org_sub"])

        # Go through the comments and award.
        try:
            for comment in post.comments:
                # Skip the comment if it isn't a parent.
                if isinstance(comment, MoreComments):
                    continue

                # Skip the comment it was deleted by the user or the user who made it no longer exists.
                try:
                    comment.body
                    comment.author.id
                except:
                    continue

                # Skip the comment if it was made by the bot.
                if comment.author == self.bot.reddit.user.me():
                    continue

                # Check if the user has already guessed on this post.
                if comment.author.name in already_awarded.keys():
                    if already_awarded[comment.author.name] == False:
                        comment.reply(reply_templates["not_allowed"])
                        already_awarded[comment.author.name] = True
                    continue

                # Check the comment to see if it was correct.
                body = comment.body.lower().strip()
                guess = body[body.find("r/") + 1:].split(" ")[0].split("]")[0] ## TODO CHECK THE FIND ON HERE
                guess = sub("^[^a-zA-Z0-9]*|[^a-zA-Z0-9]", "", guess)

                if guess == correct_subreddit:
                    # Mark that the user has guessed correctly (and have not been sent a message yet if they do a second guess on the same post)
                    already_awarded[comment.author.name] = False

                    # Reply to their comment and update their score.
                    comment.reply(reply_templates["correct"].format(points=points))
                    self.bot.points.update_score(comment.author.name, points)
                else:
                    # They guessed incorrectly.
                    comment.reply(reply_templates["incorrect"].format(correct_subreddit=correct_subreddit))
        except Exception as e:
            self.bot.sentry.capture_exception(e)
            pass

        # Delete all the post info.
        del self.pid_to_info[post_id]
        del self.pid_to_expiry[post_id]

    def check_posts(self) -> None:
        """
        Checks all the currently open posts and closes those that have expired.
        """
        print("POSTS: Checking posts.")

        posts_closed = 0
        current_timestamp = get_utc_timestamp()

        # This is copied to prevent a "dictionary changed size during iteration" error.
        currently_open_posts = self.pid_to_expiry.copy()
        for post_id, expiry_timestamp in currently_open_posts.items():
            if current_timestamp >= expiry_timestamp:
                posts_closed += 1
                self.close_post(post_id)

        # Update the wiki and leaderboard if at least one post was closed.
        if posts_closed:
            self.update_info()
            self.bot.widgets.update()

        print("POSTS: Succesfully checked posts.")
