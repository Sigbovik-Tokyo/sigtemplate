"""Utils for Templite and CodeBuilder Classes

Utility functions to make life easier.

"""

import re

def _syntax_error(msg, thing):
    """Raise a syntax error using `msg`, and showing `thing`."""
    from sigtemplate.templite import TempliteSyntaxError
    raise TempliteSyntaxError("%s: %r" % (msg, thing))


def _variable(name, vars_set):
    """Track that `name` is used as a variable.

    Adds the name to `vars_set`, a set of variable names.

    Raises an syntax error if `name` is not a valid name.

    """

    if (not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name)):
        _syntax_error("Not a valid name", name)

    vars_set.add(name)


