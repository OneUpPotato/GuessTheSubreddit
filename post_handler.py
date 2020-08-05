from re import sub
from time import sleep, time
from json import loads, dumps
from praw.models import MoreComments
from datetime import datetime, timedelta
from random import choice, sample, randint, shuffle

import settings
from sentry import capture_exception
from reddit import get_reddit, get_subreddit, get_reddit_username
from webhooks import post_submissions_webhook
from points_handler import update_leaderboard, update_score
from templates import get_post_comment_templates, get_reply_comment_templates
from helpers import format_title, get_current_utc, format_time, get_random_new_post_msg

post_types = [
    "standard", # Standard
    "multi", # Multiple Choice
    "fillblank", # Fill the blank.
    "jumbled", # Obfuscation
]

# Information of all currently open posts.
pid_to_info = {}

# IDs of active guessing posts to the expiry timestamp.
pid_to_expiry = {}

# Post IDs of submissions already posted before.
# Submissions with these ids are ignored when getting a random submission.
ignore_posts = []

# Called from load_configs in settings, on startup.
# Loads pages for pid_to_info, pid_to_expiry and ignore_posts.
def load_wiki():
    global pid_to_info, pid_to_expiry, ignore_posts
    pid_to_info = loads(get_subreddit().wiki["pidtoinfo"].content_md)
    pid_to_expiry = loads(get_subreddit().wiki["pidtoexpiry"].content_md)
    ignore_posts = loads(get_subreddit().wiki["ignoreposts"].content_md)[:100]

# Update the wiki pages.
# Stores the updated version of pid_to_info, pid_to_expiry and ignore_posts.
def update_wiki():
    get_subreddit().wiki["pidtoinfo"].edit(dumps(pid_to_info), reason="Updated list due to new post/post closure.")
    get_subreddit().wiki["pidtoexpiry"].edit(dumps(pid_to_expiry), reason="Updated list due to new post/post closure.")
    get_subreddit().wiki["ignoreposts"].edit(dumps(ignore_posts), reason="Updated list due to new post/post closure.")

# Get a random subreddit from the subreddit list.
def get_random_subreddit(exclude=[]):
    subreddit = choice(settings.get_subreddits_list())
    return subreddit if subreddit not in exclude else get_random_subreddit()

# Get a random submission from a random subreddit.
def get_random_submission():
    search_info = {"subreddit": get_random_subreddit(), "subreddits_exclude": [], "found": False}
    search_info["subreddits_exclude"].append(search_info["subreddit"])

    while not search_info["found"]:
        submissions = []
        for submission in get_reddit().subreddit(search_info["subreddit"]).top("day", limit=25):
            if submission.domain.lower() == "i.redd.it":
                submissions.append(submission)

        if len(submissions) >= 1:
            search_info["found"] = True
            random_submission = choice(submissions)
            if random_submission.id not in ignore_posts:
                return random_submission
            else:
                search_info["found"] = False
        else:
            print("Not enough submissions on /r/{}. Randomising the subreddit again.".format(search_info["subreddit"]))
            search_info["subreddits_exclude"].append(search_info["subreddit"])
            search_info["subreddit"] = get_random_subreddit(search_info["subreddits_exclude"])

# Generate comment text depending on the post type.
def generate_post_comment_text(type, subreddit):
    post_comment_templates = get_post_comment_templates()
    main_comment_text = post_comment_templates["main"]["comment_text"]

    # Setup the post type text.
    type_item = None
    if type == "multi":
        # Multiple Choice
        # List of four subreddits to choose from.
        grouped_subreddit = None
        for grouping in settings.get_settings()["settings_by_type"]["multi"]["grouped_subreddits"]:
            if subreddit in grouping:
                grouped_subreddit = str([sub for sub in grouping if sub != subreddit][0])
                break

        multi_list = sample([sub for sub in settings.get_subreddits_list() if sub != subreddit], 3) + [subreddit]
        if grouped_subreddit != None and randint(0, 1) == 1:
            del multi_list[0]
            multi_list.append(grouped_subreddit)

        shuffle(multi_list)

        type_item = post_comment_templates["post_type_text"][type].format(*multi_list)
    elif type == "fillblank":
        # Fill the Bank
        # The length of the subreddit is given.
        subreddit_len = len(subreddit)
        type_item = post_comment_templates["post_type_text"][type].format("/r/" + ("_" * subreddit_len) + f" ({subreddit_len} characters)")
    elif type == "jumbled":
        # Jumbled
        # The letters of the subreddit are jumbled.
        subreddit_chars = list(subreddit)
        shuffle(subreddit_chars)
        type_item = post_comment_templates["post_type_text"][type].format("/r/" + "".join(subreddit_chars))

    # Format the type_item into the post_type_text.
    post_type_text = ""
    if type_item != None:
        section_seperator = post_comment_templates["main"]["section_seperator"]
        post_type_text = f"{section_seperator}{type_item}{section_seperator}".rstrip()

    # Format the post closure info.
    post_close_time = (get_current_utc() + timedelta(seconds=settings.get_settings()["post_expiry_time"])).strftime("%d/%m/%Y at %H:%M")
    post_closure_info = post_comment_templates["main"]["post_closure_info"].format(date_and_time=post_close_time)

    # Format the main comment text template, and return it.
    return main_comment_text.format(header=post_comment_templates["main"]["header_default"], post_closure_source_info=post_closure_info, post_type_text=post_type_text)

# Generate comment text for when a submission is closed.
def generate_post_comment_complete_text(current_text, post_info):
    post_comment_templates = get_post_comment_templates()

    original_submission = get_reddit().submission(post_info["org_pid"])
    original_permalink = original_submission.permalink

    # Copy the post type information to use on the regenerated template.
    type_item = ""
    current_text_lines = current_text.splitlines()
    if post_info["type"] not in ["standard", "multi"]:
        type_item = current_text_lines[9].strip()
    elif post_info["type"] == "multi":
        type_item = []
        for i in range(0, 4):
            type_item.append(str(current_text_lines[10 + i].strip().replace("* /r/", "")))

    # Format the type_item into its comment template.
    post_type_text = ""
    if isinstance(type_item, list):
        post_type_text = post_comment_templates["post_type_text"][post_info["type"]].format(*type_item)
    elif type_item != "":
        post_type_text = post_comment_templates["post_type_text"][post_info["type"]].format(type_item)

    # Add the section seperators to the post_type_text
    section_seperator = post_comment_templates["main"]["section_seperator"]
    if post_type_text != "":
        post_type_text = f"{section_seperator}{post_type_text}{section_seperator}".rstrip()

    # Add the information on where the post originally came from.
    post_source_info = post_comment_templates["main"]["post_source_info"].format(subreddit=post_info["org_sub"], author=post_info["org_auth"], permalink=original_permalink)
    post_source_info = f"{section_seperator}{post_source_info}{section_seperator}"

    # Format the comment text template, and return it.
    return post_comment_templates["main"]["comment_text"].format(header=post_comment_templates["main"]["header_complete"], post_closure_source_info=post_source_info, post_type_text=post_type_text)

# Store information on a post to check it later.
def add_post_info(post_id, comment_id, type, original_submission_info):
    global pid_to_info, pid_to_expiry, ignore_posts

    # Store the information of a new post.
    pid_to_info[post_id] = {
        "type": type,
        "comment_id": comment_id,
        "org_pid": original_submission_info["id"],
        "org_sub": original_submission_info["sub"],
        "org_auth": original_submission_info["author"],
    }

    pid_to_expiry[post_id] = int(datetime.timestamp(get_current_utc()) + settings.get_settings()["post_expiry_time"])
    ignore_posts.append(original_submission_info["id"])

    # Save the new additions to the wiki.
    update_wiki()

# Submit a new post to the subreddit.
def submit_post(type=None):
    # If a type isn't specified get a random type.
    type = choice(post_types) if type == None else type.lower()

    # Get a random submission and gather the needed information for it.
    random_submission = get_random_submission()
    submission_info = {
        "id": random_submission.id,
        "sub": random_submission.subreddit.display_name.lower(),
    }

    # Try and get the author's name. If unable to the author is deleted/removed.
    try:
        submission_info["author"] = random_submission.author.name
    except:
        submission_info["author"] = "[removed/deleted]"

    # Post the submission to the subreddit.
    # Then add the relevant flair to the post.
    subreddit_post = get_subreddit().submit(
        title=format_title(random_submission.title),
        url=random_submission.url,
        nsfw=random_submission.over_18,
        spoiler=random_submission.spoiler,
    )
    subreddit_post.flair.select(settings.get_flairs()["post"][type])

    # Generate some comment text depending on the post type.
    # Then post, distinguish, lock and sticky it.
    sleep(20)
    comment = subreddit_post.reply(generate_post_comment_text(type, submission_info["sub"].lower()))
    comment.mod.distinguish(how='yes', sticky=True)
    comment.mod.lock()

    # Store the post information.
    add_post_info(
        subreddit_post.id,
        comment.id,
        type,
        submission_info,
    )

    # Send a message using the Discord webhook.
    post_submissions_webhook({
        "title": subreddit_post.title,
        "description": get_random_new_post_msg(),
        "url": "https://reddit.com{}".format(subreddit_post.permalink),
        "image": {"url": subreddit_post.url},
        "timestamp": format_time(subreddit_post.created_utc),
    })

    print("Succesfully posted.")

# Lock a post and check the comments for correct guesses.
def close_post(post_id):
    global pid_to_info, pid_to_expiry
    post_info = pid_to_info[post_id]
    correct_subreddit = sub("^[^a-zA-Z0-9]*|[^a-zA-Z0-9]", "", post_info["org_sub"].lower())

    try:
        post = get_reddit().submission(post_id)
        post.mod.lock()

        comment = get_reddit().comment(post_info["comment_id"])
        comment.edit(generate_post_comment_complete_text(comment.body, post_info))

        comment_reply_templates = get_reply_comment_templates()
        points_to_award = settings.get_settings()["points_by_type"][post_info["type"]]

        # Go through the comments and give points to those who guessed correctly.
        already_awarded = []
        for comment in post.comments:
            # If the comment is a MoreComments object skip to the next iteration.
            if isinstance(comment, MoreComments):
                continue

            # Attempt to get the comment author's name (if valid).
            commen_author_name = None
            try:
                comment_author_name = comment.author.name.lower()
            except:
                pass

            # If the comment author is the bot then skip to the next iteration.
            # If the comment author's name isn't valid then skip to the next iteration.
            if comment_author_name in [get_reddit_username().lower(), None]:
                continue

            try:
                comment_body = str(comment.body).lower().strip()
                subreddit_guess = comment_body[comment_body.find("r/") + 1:].split(" ")[0].split("]")[0]
                subreddit_guess = sub("^[^a-zA-Z0-9]*|[^a-zA-Z0-9]", "", subreddit_guess)

                # Check if the user guessed the subreddit correctly.
                if subreddit_guess == correct_subreddit:
                    # Ensure that the user hasn't already made a correct guess in this post.
                    if comment_author_name not in already_awarded:
                        already_awarded.append(comment_author_name)
                        comment.reply(comment_reply_templates["correct"].format(points=points_to_award))
                        update_score(comment_author_name, points_to_award)
                    else:
                        comment.reply(comment_reply_templates["not_allowed"])
                else:
                    # The subreddit was not guessed correctly.
                    comment.reply(comment_reply_templates["incorrect"].format(correct_subreddit=correct_subreddit))
            except:
                comment.reply(comment_reply_templates["error"])
                pass
    except Exception as e:
        capture_exception(e)
        print(f"{e} - Error closing post.")
        pass

    del pid_to_info[post_id]
    del pid_to_expiry[post_id]

# Checks all the active posts to see if any have expired.
# Ran on an interval from main.py
def check_posts():
    # A check used that will update the wiki and leaderboards if a post has been closed.
    closed_a_post = False

    # This is to prevent a "RuntimeError: dictionary changed size during iteration" error.
    currently_open_posts = pid_to_expiry.copy().items()
    for post_id, expiry_timestamp in currently_open_posts:
        if int(time()) >= expiry_timestamp:
            closed_a_post = True
            print(f"Closing post: {post_id}.")
            close_post(post_id)

    # If a post has been closed then update the wiki and leaderboard after it/any of the others have been closed.
    if closed_a_post:
        update_wiki()
        update_leaderboard()
