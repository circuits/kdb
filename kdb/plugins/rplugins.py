from os import mkdir
from hashlib import sha1
from os.path import join as path_join
from os.path import exists as path_exists
from sys import path as module_search_path


from circuits import task, Component

from funcy import first, second

from requests import get


from ..utils import log
from ..events import cmd
from ..plugin import BasePlugin


def get_url(*args, **kwargs):
    return get(*args, **kwargs)


def verify_plugin(url, path, allowed):
    response = get_url(url)
    plugin = sha1(response.content).hexdigest()
    if plugin in allowed:
        with open(path_join(path, "{0:s}.py".format(plugin)), "w") as f:
            f.write(response.content)
        return True, plugin
    return False, plugin


class RPluginsCommands(Component):

    channel = "commands:rplugins"

    def add(self, source, target, args):
        """Add a Remote Plugin

        Syntax: ADD <url>
        """

        if not args:
            yield "No URL specified."

        url = first(args.split(" ", 1))

        data = self.parent.data.rplugins
        config = self.parent.config["rplugins"]

        if url in data["enabled"]:
            yield log("Remote Plugin {0:s} already loaded!", url)
        else:
            value = yield self.call(
                task(
                    verify_plugin,
                    url,
                    config["path"],
                    data["allowed"],
                ),
                "workerprocesses"
            )

            allowed, plugin = value.value
            if allowed:
                msg = log(
                    "Remote Plugin {0:s} ({1:s}) is already authorized.",
                    url, plugin
                )
                yield msg
            else:
                data["pending"][plugin] = url

                msg = log(
                    "Remote Plugin {0:s} ({1:s}) pending authorization.",
                    url, plugin
                )
                yield msg

    def auth(self, source, target, args):
        """Authorize a Remote Plugin

        Syntax: AUTH <plugin> <password>
        """

        if not args:
            yield "No plugin specified."
            return

        tokens = args.split(" ", 2)
        plugin = first(tokens)
        password = second(tokens)

        data = self.parent.data.rplugins
        config = self.parent.config["rplugins"]

        if password != config["password"]:
            yield "Authorization failed."
            return

        if plugin in data["pending"]:
            url = data["pending"][plugin]
            del data["pending"][plugin]
            data["allowed"][plugin] = True

            value = yield self.call(
                task(
                    verify_plugin,
                    url,
                    config["path"],
                    data["allowed"],
                ),
                "workerprocesses"
            )

            allowed, plugin = value.value
            if allowed:
                msg = log(
                    "Remote Plugin {0:s} ({1:s}) successfully authorized.",
                    url, plugin
                )
                yield msg
            else:
                del data["allowed"][plugin]

                msg = log(
                    "Remote Plugin {0:s} ({1:s}) failed authorization.",
                    url, plugin
                )
                yield msg
        else:
            yield log("Remote Plugin {0:s} not found.", plugin)

    def pending(self, source, target, args):
        """Display Pending Remote Plugins

        Syntax: PENDING
        """

        data = self.parent.data.rplugins

        if not data["pending"]:
            yield "No Remote Plugins pending authorization."
        else:
            yield "Remote Plugins Pending Authorization:"
            for k, v in data["pending"].items():
                yield " {0:s} ({1:s})".format(k, v)


class Commands(Component):

    channel = "commands"

    def rplugins(self, source, target, args):
        """Manage Remote Plugins

        Syntax: RPLUGINS <command>

        See: COMMANDS rplugins
        """

        if not args:
            yield "No command specified."

        tokens = args.split(" ", 1)
        command, args = first(tokens), (second(tokens) or "")
        command = command.encode("utf-8")

        event = cmd.create(command, source, target, args)

        try:
            yield (yield self.call(event, "commands:rplugins"))
        except Exception as error:
            yield "ERROR: {0:s}".format(error)


class RPlugins(BasePlugin):
    """Remote Plugin Management

    This plugin allows the user to manage remote plugins.
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(RPlugins, self).init(*args, **kwargs)

        self.data.init(
            {
                "rplugins": {
                    "allowed": {},
                    "pending": {},
                    "enabled": {},
                }
            }
        )

        rplugins_path = self.config["rplugins"]["path"]
        if not path_exists(rplugins_path):
            mkdir(rplugins_path)

        rplugins_init_py = path_join(rplugins_path, "__init__.py")
        if not path_exists(rplugins_init_py):
            with open(rplugins_init_py, "w") as f:
                f.write("")

        if rplugins_path not in module_search_path:
            module_search_path.append(rplugins_path)

        Commands().register(self)
        RPluginsCommands().register(self)
