from time import time, sleep
from threading import Thread

class Schedular:
    def __init__(self, bot) -> None:
        self.bot = bot

        # Check for posts to close every 300 seconds (5 minutes).
        checking_thread = Thread(target=lambda: self.every(300, self.bot.posts.check_posts))
        checking_thread.start()

        # Submit a new post every 1800 seconds (30 minutes).
        submission_thread = Thread(target=lambda: self.every(1800, self.bot.posts.submit_post))
        submission_thread.start()

        self.bot.posts.submit_post("sounds")
        self.bot.posts.submit_post("revealed")

        # Post and/or check posts on start depending on the settings.
        if self.bot.settings.general["toggles"]["post_on_start"]:
            Thread(target=self.bot.posts.submit_post).start()

        if self.bot.settings.general["toggles"]["check_posts_on_start"]:
            Thread(target=self.bot.posts.check_posts).start()

    def every(self, seconds: int, task) -> None:
        """
        Runs a task every specific interval.
        :param seconds: The amount of seconds between each time the task is run.
        """
        next_time = time() + seconds
        while True:
            sleep(max(0, next_time - time()))

            try:
                task()
            except Exception as e:
                self.bot.sentry.capture_exception(e)
                pass

            next_time += (time() - next_time) // seconds * seconds + seconds
