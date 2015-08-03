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


def parse_port(s):
    ssl = s and s[0] == "+"
    port = int(s.lstrip("+"))

    return ssl, port
