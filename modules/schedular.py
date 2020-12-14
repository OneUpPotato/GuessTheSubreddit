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
from time import time, sleep
from datetime import timedelta
from threading import Thread

from utils.helpers import get_current_utc


class Schedular:
    def __init__(self, bot) -> None:
        self.bot = bot

        # Check for posts to close every 300 seconds (5 minutes).
        checking_thread = Thread(target=lambda: self.every(300, self.bot.posts.check_posts))
        checking_thread.start()

        # Submit a new post every 1800 seconds (30 minutes).
        submission_thread = Thread(target=lambda: self.every(1800, self.bot.posts.submit_post))
        submission_thread.start()

        # Handle the weekly update posts.
        weekly_update_thread = Thread(target=self.weekly_post_countdown)
        weekly_update_thread.start()

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
                if self.bot.sentry:
                    self.bot.sentry.capture_exception(e)
                else:
                    print(e)
                pass

            next_time += (time() - next_time) // seconds * seconds + seconds

    def weekly_post_countdown(self) -> None:
        """
        Posts the weekly post when it turns Monday 12AM UTC
        """
        while True:
            time = get_current_utc().replace(hour=0, minute=0, second=0, microsecond=0)
            wait_for = ((time + timedelta(days=-time.weekday(), weeks=1)) - time).total_seconds()
            sleep(wait_for)
            self.bot.posts.submit_weekly_post()
