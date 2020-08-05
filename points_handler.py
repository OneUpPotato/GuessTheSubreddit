from num2words import num2words
from praw.models import TextArea

import settings
import reddit
from sentry import capture_exception
from templates import get_leaderboard_templates

user_to_score = {}

def load_scores():
    global user_to_score
    for flair in reddit.get_subreddit().flair(limit=None):
        try:
            username = str(flair["user"].name).lower()
            user_to_score[username] = int(flair["flair_text"].split(" ")[0].replace(settings.get_flairs()["user"]["score"]["text"].format(""), ""))
        except:
            pass

def get_leaderboard_table():
    # Generate the leaderboard table.
    leaderboard_table = get_leaderboard_templates()["main"]

    top_users = sorted(user_to_score.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, user_info in enumerate(top_users):
        leaderboard_table += "\n|{}|{}|{}|".format(num2words((i + 1), to="ordinal_num"), user_info[0], user_info[1])

    return leaderboard_table

def update_score(username, amount):
    # Update a user's score by a specified amount.
    global user_to_score
    if username != None:
        score_flair_template = settings.get_flairs()["user"]["score"]
        try:
            if username not in user_to_score.keys():
                user_to_score[username] = amount
                reddit.get_subreddit().flair.set(username, score_flair_template["text"].format(amount), flair_template_id=score_flair_template["id"])
            else:
                user_to_score[username] += amount
                reddit.get_subreddit().flair.set(username, score_flair_template["text"].format(user_to_score[username]))
        except Exception as e:
            capture_exception(e)
            print("Error updating score.")
    else:
        print("Invalid username provided for score update.")

def update_leaderboard():
    try:
        print("Updating leaderboard.")

        templates = get_leaderboard_templates()

        # Get the leaderboard table.
        leaderboard_table = get_leaderboard_table()

        # Format the widget and sidebar template with the leaderboard table.
        widget_text = templates["widget"].format(leaderboard=leaderboard_table)
        sidebar_text = templates["sidebar"].format(leaderboard=leaderboard_table)

        # Attempt to update the sidebar and widget.
        reddit.get_subreddit().wiki['config/sidebar'].edit(sidebar_text)
        widget = reddit.get_subreddit().widgets.sidebar[3]
        if isinstance(widget,TextArea):
            widget.mod.update(text=widget_text)
            print("Leaderboard updated.")
        else:
            print("Unable to find the correct widget.")
    except Exception as e:
        capture_exception(e)
        print(f"{e} - Problem with updating leaderboard.")
        pass
