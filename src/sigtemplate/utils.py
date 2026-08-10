"""Utils for Templite and CodeBuilder Classes

Utility functions to make life easier.

"""

import re

class TempliteSyntaxError(Exception):
    """Raised when a syntax error within the templater engine occurs."""
    pass

def _syntax_error(
    self, msg, thing):
    """Raise a syntax error using `msg`, and showing `thing`."""
    raise TempliteSyntaxError("%s: %r" % (msg, thing))


def _variable(
    self, name, vars_set):
    """Track that `name` is used as a variable.

    Adds the name to `vars_set`, a set of variable names.

    Raises an syntax error if `name` is not a valid name.

    """

    if (not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name)):
        self._syntax_error("Not a valid name", name)

    vars_set.add(name)


