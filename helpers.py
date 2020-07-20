import yaml
from json import dumps
from pathlib import Path

from datetime import datetime
from pytz import timezone, utc

from re import sub, IGNORECASE
from random import choice

# Configs are stored in JSOC to allow for comments.
# https://github.com/eyalev/jsoc
def load_jsoc(file_path):
    text = Path(file_path).read_text()
    jsoc = yaml.safe_load(text)
    return jsoc

# Remove anything that could indicate the subreddit in the title.
def redact_title(title):
    # \s* = Ignore Whitespace
    title = sub(r"\s*🔥\s*", " ", title)
    title = sub(r"\s*\[?P(hoto)?S(hop)?Battles\]?\s*", "", title, flags=IGNORECASE)
    title = sub(r"\s*me_irl\s*", "", title, flags=IGNORECASE)
    title = sub(r"\s*woof_irl\s*", "", title, flags=IGNORECASE)
    return title

# Format a post title.
def format_title(title):
    title = str(redact_title(title).strip())[:294]
    return "[GTS] " + (title if len(title) >= 1 else "Guess The Subreddit")

# Get the current datetime in UTC.
def get_current_utc():
    return datetime.now(utc)

# Format a UNIX timestamp in ISO8601 time.
def format_time(timestamp):
    return datetime.fromtimestamp(timestamp, timezone("Etc/UTC")).isoformat()

# Return a random message saying that there's a new post.
def get_random_new_post_msg():
    return choice([
        "There's a new post to guess on!",
        "A new post has been added! :)",
        "Guessing time! There's a new post.",
    ])
