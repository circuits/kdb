# Module:   defaults
# Date:     14th May 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""defaults - System Defaults

This module contains default configuration and sane defaults for various
parts of the system. These defaults are used by the environment initially
when no environment has been created.
"""

CONFIG = {
        "server": {
            "host":         "irc.freenode.net",
            "port":         6667
        },
        "bot": {
            "nick":         "kdb",
            "ident":        "kdb",
            "name":         "Knowledge Database Bot",
            "channels":     "#circuits",
        },
        "plugins": {
            "broadcast.*":  "enabled",
            "channels.*":   "enabled",
            "core.*":       "enabled",
            "ctcp.*":       "enabled",
            "dnstools.*":   "enabled",
            "eval.*":       "enabled",
            "google.*":     "enabled",
            "greeting.*":   "enabled",
            "help.*":       "enabled",
            "irc.*":        "enabled",
            "stats.*":      "enabled",
            "swatch.*":     "enabled",
            "timers.*":     "enabled",
        },
}
