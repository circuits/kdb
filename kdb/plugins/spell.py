from enchant import request_dict


from circuits import Component


from ..plugin import BasePlugin


DEFAULT_LANGUAGE = "en_US"


class Commands(Component):

    channel = "commands"

    def spell(self, source, target, args):
        """Check the spelling of the given word.

        Syntax: SPELL <word>
        """

        if not args:
            return "No word specified."

        word = args

        if self.parent.dictionary.check(word):
            msg = "{0:s} is spelled correctly.".format(word)
        else:
            suggestions = self.parent.dictionary.suggest(word)
            msg = "{0:s} ? Try: {1:s}".format(word, " ".join(suggestions))

        return msg


class Spell(BasePlugin):
    """Spell Checker

    This plugin provides to the user a command that
    can be used to check the spelling of words and
    give suggestions for incorrectly spelled words.
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Spell, self).init(*args, **kwargs)

        self.language = DEFAULT_LANGUAGE
        self.dictionary = request_dict(self.language)

        Commands().register(self)
