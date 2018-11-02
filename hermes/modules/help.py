"""
This module creates a help screen for the user, displaying all of the commands that the bot can
understand based on the registered modules. It will by default just show the command and whether
it can be issued in pubmsg, privmsg or both. However, if the @help_message and/or @example
annotations are filled out, then it will show those as well as the command.
"""

from hermes.module import event, command, help_message


@event("privmsg", "pubmsg")
@command("help")
@help_message("Display this help message")
def show_help(bot, connection, event):
    """
    
    :param bot: 
    :type bot: hermes.Hermes
    :param connection: 
    :param event: 
    :return: 
    """
    target = event.source.nick
    connection.privmsg(target, "Hello, I'm the friendly IRC bot.")
    connection.privmsg(target, "The following commands can be private messaged to me:")
    connection.privmsg(target, "------------------")
    _show_inner_help("privmsg", bot, connection, event)
    connection.privmsg(target, "The following commands can be used in public channels:")
    connection.privmsg(target, "------------------")
    _show_inner_help("pubmsg", bot, connection, event)


def _show_inner_help(type, bot, connection, event):
    target = event.source.nick
    for name, mod in bot.modules.items():
        for func in mod.__callables__:
            if type in func.events:
                if func.admin_only is True and not bot.check_admin(event):
                    continue
                if hasattr(func, "rules"):
                    continue
                if hasattr(func, "commands"):
                    connection.privmsg(target,
                                       "Command(s): {}".format(", ".join(func.commands)))
                if func.help is not None:
                    connection.privmsg(target, "Description: {}".format(func.help))
                if len(func.examples) > 0:
                    for example in func.examples:
                        connection.privmsg(target, "Example: {}".format(example))
                connection.privmsg(target, "------------------")