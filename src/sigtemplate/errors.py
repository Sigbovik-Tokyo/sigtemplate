"""Errors for the sigtemplate class"""

class TempliteSyntaxError(Exception):
    """Raised when a syntax error within the templater engine occurs."""
    pass


class TempliteValueError(ValueError):
    """Raised when an expression won't evaluate in a template."""
    pass
