from time import time, sleep
from threading import Thread
from datetime import datetime, timedelta

from settings import load_configs, get_settings

from points_handler import update_leaderboard
from post_handler import check_posts, submit_post

# Load all the configuration files in settings.
load_configs()

# Update the leaderboard when the bot starts.
update_leaderboard()

# Check the posts when the bot starts depending on settings.
if get_settings()["check_posts_on_start"]:
    print("Checking posts on start.")
    check_posts()

# Submit a post when the bot starts depending on settings.
if get_settings()["round_30_mins_post_on_start"]:
    print("Waiting to post at the nearest next half past/hour.")
    sleep(((timedelta(hours=24) - (datetime.now() - (datetime.now() + (datetime.min - datetime.now()) % timedelta(minutes=30)))).total_seconds() % (24 * 3600)))
    submit_post()
elif get_settings()["post_on_start"]:
    print("Submitting post on start.")
    submit_post()

# Coroutine used in the checking and submitting threads.
def every(seconds, task):
    next_time = time() + seconds
    while True:
        sleep(max(0, next_time - time()))

    try:
        task()
    except:
        pass

    next_time += (time() - next_time) // seconds * seconds + seconds

# check_posts - 300 seconds = 5 minutes.
# submit_post - 1800 seconds = 30 minutes.
Thread(target=lambda: every(300, check_posts)).start()
Thread(target=lambda: every(1800, submit_post)).start()
