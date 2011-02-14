# Module:   semnet
# Date:     03th July 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Semantic Network

This plugin implements a semantic network (a kind of an AI)
that allows the user to create relationships between things
and ask questions.
"""

__version__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import re
import types
import string
import pickle

from pymills.ai.semnet import Fact, Entity, Relation, GetIsA, GetExampleOf

from circuits import handler
from pymills.misc import strToBool
from circuits.net.protocols.irc import Message

from kdb.plugin import BasePlugin

def tostr(x):

    t = type(x)
    if t == types.DictionaryType:
        return "{" + string.join(
                map(lambda k, d=x: tostr(k) + ": " + tostr(d[k]),
                    x.keys()), ", ") + "}"

    if t == types.ListType:
        return "[" + string.join(
                map(lambda i: tostr(i), x),
                ", ") + "]"

    return str(x)

class Semnet(BasePlugin):
    "Semantic Network"

    def __init__(self, *args, **kwargs):
        super(Semnet, self).__init__(*args, **kwargs)

        self.isa = GetIsA()
        self.exampleof = GetExampleOf()

        self.relations = {
                "isa": self.isa,
                "exampleOf": self.exampleof}
        self.entities = {}

        filename = os.path.join(self.env.path, "semnet.bin")
        if os.path.exists(filename):
            fp = open(filename, "rb")
            r, e = pickle.load(fp)
            self.relations.update(r)
            self.entities.update(e)
            fp.close()

    def cleanup(self):
        filename = os.path.join(self.env.path, "semnet.bin")
        fp = open(filename, "wb")
        pickle.dump((self.relations, self.entities), fp)
        fp.close()

    def cmdSEMNET(self, source, target):
        """Display the current Semantic Network
        
        Syntax: SEMNET
        """

        msg = [
                "Entities: %s" % ", ".join(self.entities.keys()),
                "Relations: %s" % ", ".join(self.relations.keys())
                ]
        return msg

    def cmdE(self, source, target, name):
        """Synonym, of ENTITY
        
        See: ENTITY
        """

        return self.cmdENTITY(source, target, name)

    def cmdENTITY(self, source, target, name):
        """Create a new entity
        
        Syntax: ENTITY <name>
        """

        if not self.entities.has_key(name):
            self.entities[name] = Entity(name)
            return "Okay"
        else:
            return [
                    "I already know something about %s" % name,
                    tostr(self.entities[name])]

    def cmdD(self, source, target, name):
        """Synonym, of DELETE
        
        See: DELETE
        """

        return self.cmdDELETE(source, target, name)

    def cmdDELETE(self, source, target, name):
        """Delete an existing entity
        
        Syntax: DELETE <name>
        """

        if self.entities.has_key(name):
            del self.entities[name]
            return "Okay"
        else:
            return "I don't know anything about %s" % name

    def cmdR(self, source, target, name, transitive="yes",
            opposite=None):
        """Synonym, of RELATION
        
        See: RELATION
        """

        return self.cmdRELATION(source, target, name, transitive,
                opposite)

    def cmdRELATION(self, source, target, name, transitive="yes",
            opposite=None):
        """Create a new relationship
        
        Syntax: RELATION <name> [<transitive>] [<opposite>]
        """

        if opposite is None:
            self.relations[name] = Relation(
                    name, strToBool(transitive))
        else:
            self.relations[name] = Relation(
                    name, strToBool(transitive))
            self.relations[opposite] = Relation(
                    opposite, strToBool(transitive),
                    self.relations[name])

        return "Okay"

    @handler("message")
    def onMESSAGE(self, source, target, message):

        addressed, target, message = self.isAddressed(
                source, target, message)

        if addressed:

            if type(target) == tuple:
                target = target[0]

            m = re.match(
                    "^(?P<agent>[a-zA-Z0-9_]+) "
                    "(?P<relation>[a-zA-Z0-9_]+) ?\?",
                    message)
            if m is not None:
                d = m.groupdict()
                if self.entities.has_key(d["agent"]) and \
                        self.relations.has_key(d["relation"]):
                    agent = self.entities[d["agent"]]
                    relation = self.relations[d["relation"]]
                    self.push(Message(
                        target,
                        tostr(agent.objects(relation))),
                        "PRIVMSG")
                else:
                    self.push(Message(target, "I don't understand."), "PRIVMSG")
                    if not self.entities.has_key(d["agent"]):
                        self.push(Message(
                            target,
                            "What is a %s ?" % d["agent"]), "PRIVMSG")
                    if not self.relations.has_key(d["relation"]):
                        self.push(Message(
                            target,
                            "What does %s mean ?" % d["relation"]), "PRIVMSG")

                return

            m = re.match(
                    "^(?P<agent>[a-zA-Z0-9_]+) "
                    "(?P<relation>[a-zA-Z0-9_]+) "
                    "(?P<object>[a-zA-Z0-9_]+) ?\?",
                    message)
            if m is not None:
                d = m.groupdict()
                if self.entities.has_key(d["agent"]) and \
                        self.relations.has_key(d["relation"]) and \
                        self.entities.has_key(d["object"]):
                    agent = self.entities[d["agent"]]
                    relation = self.relations[d["relation"]]
                    object = self.entities[d["object"]]

                    if relation(agent, object):
                        self.push(Message(target, "yes"), "PRIVMSG")
                    else:
                        self.push(Message(target, "no"), "PRIVMSG")
                else:
                    self.push(Message(
                        target,
                        "I don't understand."), "PRIVMSG")
                    if not self.entities.has_key(d["agent"]):
                        self.push(Message(
                            target,
                            "What is a %s ?" % d["agent"]), "PRIVMSG")
                    if not self.relations.has_key(d["relation"]):
                        self.push(Message(
                            target,
                            "What does %s mean ?" % d["relation"]), "PRIVMSG")
                    if not self.entities.has_key(d["object"]):
                        self.push(Message(
                            target,
                            "What is a %s ?" % d["object"]), "PRIVMSG")

                return

            m = re.match(
                    "^(?P<agent>[a-zA-Z0-9_]+) "
                    "(?P<relation>[a-zA-Z0-9_]+) "
                    "(?P<object>[a-zA-Z0-9_]+)",
                    message)
            if m is not None:
                d = m.groupdict()
                if self.entities.has_key(d["agent"]) and \
                        self.relations.has_key(d["relation"]) and \
                        self.entities.has_key(d["object"]):
                    agent = self.entities[d["agent"]]
                    relation = self.relations[d["relation"]]
                    object = self.entities[d["object"]]

                    if relation(agent, object):
                        self.push(Message(
                            target,
                            "I already knew that."), "PRIVMSG")
                    else:
                        Fact(agent, relation, object)
                        self.push(Message(target, "Okay"), "PRIVMSG")
                else:
                    self.push(Message(
                        target,
                        "I don't understand."), "PRIVMSG")
                    if not self.entities.has_key(d["agent"]):
                        self.push(Message(
                            target,
                            "What is a %s ?" % d["agent"]), "PRIVMSG")
                    if not self.relations.has_key(d["relation"]):
                        self.push(Message(
                            target,
                            "What does %s mean ?" % d["relation"]), "PRIVMSG")
                    if not self.entities.has_key(d["object"]):
                        self.push(Message(
                            target,
                            "What is a %s ?" % d["object"]), "PRIVMSG")

                return
