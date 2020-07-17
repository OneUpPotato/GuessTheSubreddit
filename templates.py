from textwrap import dedent

templates = {
    # Comment Templates
    "comments": {
        "post": {
            "main": {
                # The main comment template.
                "comment_text": dedent("""
                    {header}

                    Please note that only top-level comments will be checked by the bot.

                    {post_closure_source_info}{post_type_text}

                    [Click here to learn more about this subreddit.](https://reddit.com/r/guessthesubreddit/wiki/index)
                """).strip(),

                # The headers that are used in the comment.
                "header_default": "**Guessing is still open for this post. Please go ahead and have a go.**",
                "header_complete": "**~~Guessing is still open for this post. Please go ahead and have a go.~~**",

                # Information on when the post closes.
                "post_closure_info": "This post closes on {date_and_time} UTC ^(D/M/Y)",

                # The text that is added once a post has been closed.
                "post_source_info": dedent("""
                    The post came from the subreddit >!/r/{subreddit}!<

                    [You can find the post (made by /u/{author}) here.]({permalink})
                """).strip(),

                # A section seperator.
                "section_seperator": "\n\n&#x200B;\n\n",
            },
            "post_type_text": {
                "multi": dedent("""
                    *Possible Subreddits:*

                    * /r/{}
                    * /r/{}
                    * /r/{}
                    * /r/{}
                """).strip(),

                "fillblank": dedent("""
                    *Fill in the Blank*

                    {}
                """).strip(),

                "jumbled": dedent("""
                    *Unscramble the Letters*

                    {}
                """).strip(),
            },
        },
        "reply": {
            "correct": "**Result:** >!CORRECT - Your score has been increased. (+{points} points)!<",
            "incorrect": "**Result:** >!INCORRECT - The correct subreddit was /r/{correct_subreddit}!<",
            "error": "**Result:** There was a problem with processing your comment.",
            "not_allowed": "**Result:** !>You've already guessed correctly on this post.!<",
        },
    },

    # Templates for the Leaderboard
    "leaderboard": {
        # The main leaderboard template, using in both the widget and sidebar.
        "main": dedent("""
            |**Place**|**Username**|**Points**|
            |:-:|:-:|:-:|
        """).strip(),

        # The widget template.
        "widget": "{leaderboard}",

        # The sidebar template.
        "sidebar": dedent("""
            # Rules
            1. Remain civilised.

            2. Don't ruin it/cheat.

            3. Please report broken posts.

            # How does this subreddit work?

            A post is made by the bot, /u/GTSBot, every 30 minutes.

            A certain amount of time is given for people to try and guess what subreddit that post has come from. This time is currently 6 hours.

            After six hours, the post will be locked and the comments will be sorted through to see who guessed correctly. Those who guessed correct will get a score increase.

            We currently suggest that you sort by new when looking for posts.

            [You can learn more about how it works on our wiki.](https://www.reddit.com/r/guessthesubreddit/wiki/index)

            # Where can I suggest ideas?

            You can leave a comment on any mod/meta thread, send a modmail to this subreddit, or [join the Discord.](https://discord.gg/RCtd7qx)

            # Who made the banner and icon?

            The current icon was made by u/mohagthemoocow, and the banner was made by myself.

            # Who made /u/GTSBot?

            The bot was made by myself (u/OneUpPotato). Feel free to message me with any suggestions that you have for it, or alternatively comment them in the suggestion thread mentioned above.

            # Points Leaderboard

            {leaderboard}
        """).strip(),
    }
}

def get_templates():
    return templates

def get_post_comment_templates():
    return templates["comments"]["post"]

def get_reply_comment_templates():
    return templates["comments"]["reply"]

def get_leaderboard_templates():
    return templates["leaderboard"]
