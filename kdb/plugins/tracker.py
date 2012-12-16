# Module:   tracker
# Date:     16th December 2012
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Tracker (Pivotal Tracker)

This plugin provides access to a Pivotal Tracker project and it's stories.

[tracker]
token = 3a5a7a485b55bf9c1f22e97570dfb384
project = circuits
"""

__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from pyvotal import PTracker

from kdb.plugin import BasePlugin


class Tracker(BasePlugin):
    """Tracker (Pivotal Tracker) Plugin

    Provides commands for working with a Pivotal Tracker Project.
    See: commands tracker
    """

    tpl = "{0:s} {1:d} ({2:s}) - {3:s}"

    def __init__(self, env):
        super(Tracker, self).__init__(env)

        token = self.env.config.get("tracker", "token", None)
        if token is None:
            raise Exception("API Token not configured")

        self.pt = PTracker(token=token)
        self.project = None
        self.stories = []

    def format_story(self, story):
        assigned = "*" if story.owned_by is None else " "
        estimate = "{0:d}".format(story.estimate) \
                if story.estimate is not None else "?"
        return self.tpl.format(assigned, story.id, estimate, story.name)

    def cmdSTORIES(self, source, target, id=None):
        """...

        Syntax: STORIES [id]
        """

        id = id or self.env.config.get("tracker", "project", None)
        if id is None:
            return "Project ID not configured or unspecified."

        try:
            id = int(id)
        except ValueError:
            pass

        if isinstance(id, basestring):
            projects = [project for project in self.pt.projects.all() \
                    if project.public and project.name == id]
            if not projects:
                return "Specified project name not found"
            id = projects[0].id

        self.project = project = self.pt.projects.get(id)
        self.stories = stories = project.stories.all()

        return [self.format_story(story) for story in stories]

    def cmdSTORY(self, source, target, id=None):
        """...

        Syntax: STORY id
        """

        if not self.stories:
            return "No stories found! Need to run STORIES?"

        try:
            id = int(id)
        except ValueError:
            return "Story ID must be a number!"

        story = [story for story in self.stories if story.id == id]
        if not story:
            return "No story by that ID"

        story = story[0]

        msgs = []
        msgs.append(self.format_story(story))
        msgs.append("Current State: {0:s}".format(story.current_state))
        msgs.append("Requested By:  {0:s}".format(story.requested_by))
        msgs.append("Story Type:    {0:s}".format(story.story_type))
        msgs.append("Owned By:      {0:s}".format(story.owned_by))
        msgs.append(story.description)

        return msgs
