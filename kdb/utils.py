# Module:   utils
# Date:     8th April 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Utilities"""


import sys


def log(message, *args, **kwargs):
    try:
        output = message.format(*args, **kwargs)
        sys.stderr.write("{0:s}\n".format(output))
        sys.stderr.flush()
    except Exception as e:
        output = "ERROR: {0:s}\n".format(e)
        sys.stderr.write(output)
        sys.stderr.flush()
    finally:
        return output
