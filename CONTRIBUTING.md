# GuessTheSubreddit Contributing Guide

First off, I'd like to thank you for considering to contribute to GuessTheSubreddit.

Below is some information on running and setting up your environment. If you'd like to further discuss development of the bot, then the [Discord guild](https://discord.gg/nMgNDQS) may be the best place.

- - -

## Setting up your environment.

#### Configuration Files
* Copy the ``.env.example`` file and rename it to ``.env``
    * The ``REDDIT_CLIENT_ID`` and ``REDDIT_CLIENT_SECRET`` are found in your Reddit [Developer Applications](https://old.reddit.com/prefs/apps/) after creating one.
    * You can generate a ``REDDIT_REFRESH_TOKEN`` using [this Python script.](https://praw.readthedocs.io/en/latest/tutorials/refresh_token.html)
    * **(optional)** The ``DISCORD_SUBMISSIONS_WEBHOOK`` is the URL of a webhook in a Discord channel.
        * A notification will be sent for new posts here.
    * **(optional)** The ``SENTRY_URL`` is your [Sentry project's](https://sentry.io) ingest URL.
* Copy the ``settings.yml.example`` file and rename it to ``settings.yml``
    * Change the ``subreddit`` to your testing subreddit's name (without the r/).
    * Set the flair ids to the ones on your testing subreddit.
* Copy the ``subreddits.yml.example`` file and rename it to ``subreddits.yml``
    * Optionally, you can populate it with more subreddits.

#### Testing Subreddit
* Create a text widget and order it as your fourth widget.
* Create flairs for the post types and put their ids in the ``settings.yml`` file.
* Create wiki pages named the following:
    * "pidtoinfo"
    * "pidtoexpiry"
    * "ignoreposts"

- - -

## Running the Bot

After configuring your environment, you can install the bot's requirements by running:

``pip install -r requirements.txt``

and start the bot using:

``python main.py``
