# Module:   gtalk
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Google Talk Plugin

This plugin provides an interface and client to the Google
Talk servers using the XMPP protocol. This plugin enables
communication via Google Talk.

[gtalk]
user = kdb
password = foobar
"""

__version__ = "0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from time import sleep

import xmpp

from circuits.net.protocols.irc import Message

from kdb.plugin import BasePlugin

class GTalk(BasePlugin):

    """Google Talk Plugin

    This plugin provides an interface and client to the Google
    Talk servers using the XMPP protocol. This plugin enables
    communication via Google Talk.

    See: commands gtalk
    """

    def __init__(self, env):
        super(GTalk, self).__init__(env)

        self._username = self.env.config.get("gtalk", "username", "kdbbot")
        self._password = self.env.config.get("gtalk", "password", "semaj2891")
        self._name = "kdb"

        self._client = xmpp.Client("gmail.com", debug=[])
        self.start()

    def __tick__(self):
        if self._client.isConnected():
            if hasattr(self._client, "Process"):
                self._client.Process()
                sleep(0.1)
        else:
            self._client.connect(server=("gmail.com", 5223))
            self._client.auth(self._username, self._password, self._name)
            self._client.RegisterHandler("message", self.messageHandler)
            self._client.sendInitPresence()
            sleep(1)

    def cleanup(self):
        self.stop()

    def sendMsg(self, to, message):
        self._client.send(xmpp.Message(to, message))

    def messageHandler(self, cnx, message):
        text = message.getBody()
        user = message.getFrom()

        if text:
            text = text.strip()
            self.env.log.debug("<%s> %s" % (user, text))

            if " " in text:
                command, args = text.split(" ", 1)
            else:
                command, _ = text, ""

            command = command.upper()

            if command == "SUBSCRIBE":
                self._client.Roster.Authorize(user)
                reply = "Authorized."
            else:
                e = Message(str(user), self("getNick"), text)
                reply = self.send(e, "message", self.channel)
                self.env.log.debug("Reply: %s" % reply)

            if type(reply) == list:
                reply = "\n".join(reply)

            self.sendMsg(user, reply)
