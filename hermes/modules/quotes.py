"""
Module to provide randomised quotes.
Administration is available  via PM from staff
"""
import re
import random

from hermes.module import event, command, rule
from pprint import pprint, pformat

key = "quotes"

def setup(bot):
    if bot.storage[key] is None:
        bot.storage[key] = dict()


@event("pubmsg", "privmsg")
@command("quote")
def quote_admin(bot, connection, event):
    """

    :param bot:
    :type bot: hermes.Hermes
    :param connection:
    :param event:
    :return:
    """
    nick = event.source.nick
    user = event.source.user
    host = event.source.host
    chan = event.target

    if event.type == 'pubmsg':
        target = event.source.nick if event.type == 'privmsg' else event.target
        if len(bot.storage[key]) > 0:
            connection.privmsg(target, random.choice(list(bot.storage[key].values())))
        return

    if not check_auth(bot, connection, host, nick, False):
        return

    command = None if len(event.args) == 0 else event.args[0]
    args = None if len(event.args) < 2 else event.args[1:]

    if command == 'add':
        quote_add(bot, connection, event, args)
    elif command == 'del':
        quote_del(bot, connection, event, args)
    elif command == 'list' or command is None:
        quote_list(bot, connection, event, args)


def quote_add(bot, connection, event, args):
    trigger = None if args is None or len(args) == 0 else args[0]
    message = None if args is None or len(args) < 2 else args[1:]
    if trigger is None or message is None:
        connection.notice(event.source.nick, "Please specify a name and message.")
        return

    if trigger in bot.storage[key]:
        connection.privmsg(event.source.nick, "Quote {0} updated.".format(trigger))
    else:
        connection.privmsg(event.source.nick, "Quote {0} added.".format(trigger))

    bot.storage[key][trigger] = " ".join(message)


def quote_del(bot, connection, event, args):
    trigger = None if args is None or len(args) == 0 else args[0]
    if trigger is None:
        connection.notice(event.source.nick, "Please specify a name.")
        return

    if trigger in bot.storage[key]:
        connection.notice(event.source.nick, "Quote {0} deleted.".format(trigger))
        del bot.storage[key][trigger]
    else:
        connection.notice(event.source.nick, "Couldn't find quote {0}.".format(trigger))


def quote_list(bot, connection, event, args):
    connection.notice(event.source.nick, "Quotes:")
    for trigger in bot.storage[key].keys():
        connection.notice(event.source.nick, "{0}: {1}".format(trigger,
            bot.storage[key][trigger]))


def check_auth(bot, connection, host, nick, prompt):
    split_host = host.split(".")
    if len(split_host) != 4:
        return False

    if host.endswith(bot.config.site.tld):
        # Make sure that the one issuing the command is authorized to do so
        user = bot.api.get_user(split_host[0])
        if user is None:
            if prompt:
                connection.notice(nick, "You must be authed through the bot to administer \
                        quotes.")
            return False

        if user['Level'] >= bot.config.quote.min_level:
            return True
        else:
            if prompt:
                connection.notice(nick, "You are not authorized to do this command!")
            return False


