<div align="center">
  <h1>GuessTheSubreddit</h1>
  <p>The source code behind the bot that runs <a href="https://reddit.com/r/guessthesubreddit">r/GuessTheSubreddit.</a></p>
</div>

## Contributing
Please feel free to help contribute to this bot :)

Here are some instructions on how to set up things on your end:
* For the configuration files:
  * Copy the ``.env.example`` file and rename it to ``.env``
    * Then fill it with the needed information.
  * Copy the ``settings.yml.example`` file and rename it to ``settings.yml``
    * Then swap the flair ids and change the subreddit name.
  * Copy the ``subreddits.yml.example`` file and rename it to ``subreddits.yml``
    * (optional) Populate it with more subreddits.
* On your testing subreddit:
  * Create a text widget and order it as your fourth widget.
  * Create wiki pages named the following:
    * "pidtoinfo"
    * "pidtoexpiry"
    * "ignoreposts"

## License
This repository has been released under the [Apache License 2.0.](https://github.com/OneUpPotato/GuessTheSubreddit/blob/master/LICENSE)
