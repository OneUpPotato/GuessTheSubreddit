import praw

import settings

reddit_instance = praw.Reddit(**settings.get_reddit_login_info(), user_agent="GuessTheSubreddit Bot v2.0 (by u/OneUpPotato)")
print(f"Succesfully accessed Reddit as u/{reddit_instance.user.me().name}")

def get_reddit():
    return reddit_instance

def get_reddit_username():
    return reddit_instance.user.me().name

def get_subreddit():
    return reddit_instance.subreddit(settings.get_subreddit_name())
