# Plugin:   google
# Date:     10th April 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Google

Plugin to perform Googles searches.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from apiclient.discovery import build

from circuits import Component

from funcy import first


from ..plugin import BasePlugin


class Commands(Component):

    channel = "commands"

    def __init__(self, *args, **kwargs):
        super(Commands, self).__init__(*args, **kwargs)

        self.service = build(
            "customsearch",
            "v1",
            developerKey="AIzaSyBfx6wfwHf2Br_zFKqGsDzFKvm_XXJQLQQ"
        )

    def google(self, source, target, args):
        """Perform a google search and return the first result.

        Syntax: GOOGLE <search>
        """

        if not args:
            return "No search terms specified."

        q = args

        results = self.service.cse().list(
            q=q, cx='017576662512468239146:omuauf_lfve',
        ).execute()

        item = first(results.get("results", []))

        return (item and item["link"]) or "No results found."


class Google(BasePlugin):
    """Google Plugin

    Perform a google search and return the results.

    See: HELP google
    """

    def init(self, *args, **kwargs):
        super(Google, self).init(*args, **kwargs)

        Commands().register(self)
