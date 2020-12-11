"""
Copyright (c) 2020 OneUpPotato

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from praw.models import TextArea


class Widgets:
    def __init__(self, bot) -> None:
        self.bot = bot

        # Update the widgets on start.
        self.update()

    def update(self) -> None:
        """
        Updates the sidebar widget and leaderboard.
        """
        points_leaderboard = self.bot.points.generate_leaderboard_table()

        # Format the widget and sidebar templates with the leaderboard table.
        templates = self.bot.settings.general["templates"]["sidebars"]
        widget_text = templates["widget"].format(leaderboard=points_leaderboard)
        sidebar_text = templates["sidebar"].format(leaderboard=points_leaderboard)

        # Attempt to update the sidebar.
        self.bot.reddit.main_subreddit.wiki['config/sidebar'].edit(sidebar_text)

        # Attempt to update the widget.
        widget = self.bot.reddit.main_subreddit.widgets.sidebar[3]
        if isinstance(widget, TextArea):
            widget.mod.update(text=widget_text)
        else:
            print("WIDGETS: Unable to find the correct widget.")

        print("WIDGETS: Updated the sidebar and widget.")
