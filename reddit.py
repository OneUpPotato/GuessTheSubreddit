import praw

import settings

reddit_instance = praw.Reddit("GuessTheSubreddit", user_agent="GuessTheSubreddit Bot v1.1 (by u/OneUpPotato)")

def get_reddit():
    return reddit_instance

def get_reddit_username():
    return reddit_instance.user.me().name

def get_subreddit():
    return reddit_instance.subreddit(settings.get_subreddit_name())
