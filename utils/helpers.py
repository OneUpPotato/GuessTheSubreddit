from praw.models import Submission

from typing import Union

from json import dumps
from yaml import safe_load

from random import choice
from requests import post
from re import sub, IGNORECASE

from pytz import utc
from datetime import datetime

def load_yaml(filepath: str) -> Union[dict, list]:
    """
    Attempts to load and parse YAML from a file.
    :param filepath: The name of the file to load.
    :return: The loaded file.
    """
    yaml = None
    try:
        with open(filepath, encoding="utf-8") as file:
            yaml = safe_load(file.read())
    except Exception as e:
        print(f"Error loading file: {filepath} - {e}")
        pass
    return yaml

def redact_title(title: str) -> str:
    """
    Remove anything that could indicate the subreddit in the title.
    \s* = Ignore Whitespace
    :return
    """
    title = sub(r"\s*🔥\s*", " ", title)
    title = sub(r"\s*\[?P(hoto)?S(hop)?Battles\]?\s*", "", title, flags=IGNORECASE)
    title = sub(r"\s*me_irl\s*", "", title, flags=IGNORECASE)
    title = sub(r"\s*woof_irl\s*", "", title, flags=IGNORECASE)
    title = sub(r"\s*maybe maybe( maybe)?(...)?\s*", "", title, flags=IGNORECASE)
    return title

def format_title(title: str) -> str:
    """
    Format a title for the guessing post.
    :return: The formatted title.
    """
    title = redact_title(title).strip()[:294]
    return "[GTS] " + (title if len(title) >= 1 else "Guess The Subreddit")

def format_time(timestamp: int) -> str:
    """
    Format a UNIX timestamp in ISO8601 time.
    :return: The formatted time.
    """
    return datetime.fromtimestamp(timestamp, utc).isoformat()

def get_current_utc() -> datetime:
    """
    Get the datetime in UTC.
    :return: The current datetime in UTC.
    """
    return datetime.now(utc)

def get_utc_timestamp() -> int:
    """
    Get the current UTC timestamp.
    :return: The current UTC timestamp.
    """
    return int(datetime.timestamp(get_current_utc()))

def post_webhook(url: str, embed: dict) -> None:
    """
    Send an embed using a webhook.
    """
    post(
        url,
        data=dumps(
            {
                "embeds": [embed],
            }
        ),
        headers={
            "Content-Type":"application/json"
        },
    )
