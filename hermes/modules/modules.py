"""
Admin module that helps to deal with other modules.
"""
from hermes.module import privmsg, command, admin_only
from hermes.loader import load_module


@admin_only()
@privmsg()
@command("list_modules")
def list_modules(bot, connection, event):
    connection.privmsg(event.source.nick, "Loaded modules:")
    for mod in bot.modules:
        connection.privmsg(event.source.nick, "-> {}".format(mod))


@admin_only()
@privmsg()
@command("reload")
def reload_module(bot, connection, event):
    """

    :param bot: 
    :type bot: hermes.Hermes
    :param connection: 
    :param event: 
    :return: 
    """
    modules = [arg.lower() for arg in event.args]
    for mod in modules:
        if mod not in bot.modules:
            connection.privmsg(event.source.nick, "Unknown module: {}".format(mod))
            continue
        # noinspection PyBroadException
        try:
            load_module(bot.modules, bot.modules[mod].__mod_path__)
            if hasattr(bot.modules[mod], 'setup'):
                bot.modules[mod].setup(bot)
            bot.logger.info("-> Reloaded module: {}".format(mod))
            connection.privmsg(event.source.nick, "Reloaded module: {}".format(mod))
        except:
            bot.logger.exception("-> Failed to reload module: {}".format(mod))
            connection.privmsg(event.source.nick, "Failed to reload module: {}".format(mod))
