# Module:   main
# Date:     12th July 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au
#
# Borrowed from sahriswiki (https://sahriswiki.org/)
# with permission from James Mills, prologic at shortcircuit dot net dot au

"""Main

Main entry point responsible for configuring and starting the application.
"""

import sys
from os.path import basename


from procname import setprocname


from circuits.app import Daemon
from circuits import Manager, Debugger


from .core import Core
from .config import Config


def main():
    setprocname(basename(sys.argv[0]))

    config = Config()

    manager = Manager()

    if config.get("debug"):
        Debugger(
            events=config.get("verbose"),
            file=config.get("errorlog")
        ).register(manager)

    if config.get("daemon"):
        manager += Daemon(config.get("pidfile"))

    Core(config).register(manager)

    manager.run()


if __name__ == "__main__":
    main()
