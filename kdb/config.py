# Module:   config
# Date:     12th July 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au
#
# Borrowed from sahriswiki (https://sahriswiki.org/)
# with permission from James Mills, prologic at shortcircuit dot net dot au


"""Configuration Handling

Supports configuration of options via the command-line
and/or a configuration file. Optiona read form
configuration file override those given via command line options.
"""


from os import environ
from warnings import warn
from os.path import exists
from ConfigParser import ConfigParser
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


import reprconf
from . import plugins
from .version import version


class Config(reprconf.Config):

    prefix = "KDB_"

    def __init__(self, file=None, **kwargs):
        super(Config, self).__init__(file, **kwargs)

        self.parse_options()
        self.parse_environ()

    def parse_environ(self):
        """Check the environment variables for options."""

        config = {}

        for key, value in environ.iteritems():
            if key.startswith(self.prefix):
                name = key[len(self.prefix):].lower()
                config[name] = value

        self.update(config)

    def parse_options(self):
        parser = ArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter,
            version=version,
        )

        add = parser.add_argument

        add(
            "--config", action="store", default=None,
            dest="config", metavar="FILE", type=str,
            help="read configuration from FILE"
        )

        add(
            "--debug", action="store_true", default=False,
            dest="debug",
            help="enable debugging mode"
        )

        add(
            "--daemon", action="store_true", default=False,
            dest="daemon",
            help="run as a background process"
        )

        add(
            "--verbose", action="store_true", default=False,
            dest="verbose",
            help="enable verbose logging"
        )

        add(
            "--errorlog", action="store", default=None,
            dest="errorlog", metavar="FILE", type=str,
            help="store debug and error logs in FILE"
        )

        add(
            "--pidfile", action="store", default="kdb.pid",
            dest="pidfile", metavar="FILE", type=str,
            help="write process id to FILE"
        )

        add(
            "-c", "--channel",
            action="append", default=["#circuits"], dest="channels",
            help="Channel to join (multiple allowed, or comma separated)"
        )

        add(
            "-n", "--nick",
            action="store", default="kdb", dest="nick",
            help="Nickname to use"
        )

        add(
            "-p", "--password",
            action="store", default=None, dest="password",
            help="Password to use when connecting"
        )

        add(
            "--plugin",
            action="append", default=plugins.DEFAULTS, dest="plugins",
            help="Plugin to load (multiple allowed)"
        )

        add(
            "host",
            action="store", nargs="?", default="irc.freenode.net",
            type=str, metavar="HOST",
            help="Host to connect to"
        )

        add(
            "port",
            action="store", nargs="?", default=6667, type=int, metavar="PORT",
            help="Port to connect to"
        )

        namespace = parser.parse_args()

        if namespace.config is not None:
            filename = namespace.config
            if exists(filename):
                config = reprconf.as_dict(str(filename))
                for option, value in config.pop("globals", {}).items():
                    if option in namespace:
                        self[option] = value
                    else:
                        warn("Ignoring unknown option %r" % option)
                self.update(config)

        for option, value in namespace.__dict__.items():
            if option not in self and value is not None:
                self[option] = value

    def reload_config(self):
        filename = self.get("config")
        if filename is not None:
            config = reprconf.as_dict(filename)
            config.pop("global", None)
            self.update(config)

    def save_config(self, filename=None):
        if filename is None:
            filename = self.get("config", "kdb.ini")

        parser = ConfigParser()
        parser.add_section("globals")

        for key, value in self.items():
            if isinstance(value, dict):
                parser.add_section(key)
                for k, v in value.items():
                    parser.set(key, k, repr(v))
            else:
                parser.set("globals", key, repr(value))

        with open(filename, "w") as f:
            parser.write(f)
