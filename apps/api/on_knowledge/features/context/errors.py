"""Actionable context failures before a generation provider is called."""


class ContextUnavailable(Exception):
    """The canonical saved document cannot be read; search chunks cannot replace it."""


class ContextTooLarge(Exception):
    """No complete selected block fits the available generation budget."""
