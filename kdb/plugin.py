# Module:   plugin
# Date:     17th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Base Plugin

This module provides the basic infastructure for kdb
plugins. Plugins should sub-class BasePlugin.
"""


from circuits import BaseComponent


class BasePlugin(BaseComponent):

    channel = "bot"

    def init(self, bot, data, config):
        self.bot = bot
        self.data = data
        self.config = config
