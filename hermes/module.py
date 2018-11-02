"""
Module defines various decorators we can assign to given module functions so that we have a nice
pluggable interface for expanding the bots abilities and functions in a way that doesn't actually
mean we have to hack apart the core bot code.
"""


def pubmsg():
    """
    Decorator 
    :return: 
    """
    def add_attribute(func):
        if not hasattr(func, "events"):
            func.events = []
        func.events.append("pubmsg")
        return func
    return add_attribute


def privmsg():
    """
    Defines a function that should only be run when we've received a private message
    :return: 
    """
    def add_attribute(func):
        if not hasattr(func, "events"):
            func.events = []
        func.events.append("privmsg")
        return func
    return add_attribute


def command(*commands):
    def add_attribute(func):
        if not hasattr(func, "commands"):
            func.commands = []
        func.commands.extend(commands)
        return func
    return add_attribute


def event(*events):
    def add_attribute(func):
        if not hasattr(func, "events"):
            func.events = []
        func.events.extend(events)
        return func
    return add_attribute


def rule(regex, flags=0):
    def add_attribute(func):
        if not hasattr(func, "rules"):
            func.rules = []
        func.rules.append([regex, flags])
        return func
    return add_attribute


def help_message(message):
    def add_attribute(func):
        func.help = message
        return func
    return add_attribute


def example(*examples):
    def add_attribute(func):
        if not hasattr(func, "examples"):
            func.examples = []
        func.examples.extend(examples)
        return func
    return add_attribute


def admin_only():
    def add_attribute(func):
        func.admin_only = True
        return func
    return add_attribute


def disabled():
    def add_attribute(func):
        func.disabled = True
        return func
    return add_attribute
