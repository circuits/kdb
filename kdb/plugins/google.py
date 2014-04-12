# Plugin:   google
# Date:     10th April 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Google

Plugin to perform Googles searches.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from json import loads


from circuits import task, Component

from requests import get


from ..plugin import BasePlugin


def get_url(*args, **kwargs):
    return get(*args, **kwargs)


class Commands(Component):

    channel = "commands"

    def __init__(self, *args, **kwargs):
        super(Commands, self).__init__(*args, **kwargs)

        self.url = "http://ajax.googleapis.com/ajax/services/search/web"

    def google(self, source, target, args):
        """Perform a google search and return the first result.

        Syntax: GOOGLE <search>
        """

        if not args:
            yield "No search terms specified."

        q = args

        value = yield self.call(
            task(
                get_url,
                self.url,
                params={"v": "1.0", "q": q}
            ),
            "workerthreads"
        )

        response = value.value
        response.raise_for_status()
        data = loads(response.content)["responseData"]

        yield "Total results: {0:s}".format(
            data["cursor"]["estimatedResultCount"]
        )

        hits = data["results"]
        yield 'Top {0:d} hits:'.format(len(hits))
        for i, hit in enumerate(hits):
            yield " {0:d}. {1:s}".format((i + 1), hit["url"])
        yield "For more results, see: {0:s}".format(
            data["cursor"]["moreResultsUrl"]
        )


class Google(BasePlugin):
    """Google Plugin

    Perform a google search and return the results.

    See: HELP google
    """

    def init(self, *args, **kwargs):
        super(Google, self).init(*args, **kwargs)

        Commands().register(self)
