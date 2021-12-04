"""
Module to provide FLS with canned responses.
Administration is available from the designated FLS channel or via PM from FLS / staff
"""
import re

from hermes.module import event, command, rule
from pprint import pprint, pformat

key = "canned_responses"

def setup(bot):
    if bot.storage[key] is None:
        bot.storage[key] = dict()


@event("pubmsg", "privmsg")
@rule(r'^[!\.][a-zA-Z0-9]+')
def can_trigger(bot, connection, event, match):
    trigger = event.cmd.lower().strip('!.')
    target = event.source.nick if event.type == 'privmsg' else event.target
    if trigger in bot.storage[key]:
        connection.privmsg(target, bot.storage[key][trigger])


@event("pubmsg", "privmsg")
@command("can")
def can_admin(bot, connection, event):
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

    if event.type == 'privmsg':
        if not check_auth(bot, connection, host, nick, False):
            return
    else:
        if not chan.strip('#').lower() == bot.config.fls.channel.lower():
            return

    command = None if len(event.args) == 0 else event.args[0]
    args = None if len(event.args) < 2 else event.args[1:]

    if command == 'add':
        can_add(bot, connection, event, args)
    elif command == 'del':
        can_del(bot, connection, event, args)
    elif command == 'list' or command is None:
        can_list(bot, connection, event, args)


def can_add(bot, connection, event, args):
    trigger = None if args is None or len(args) == 0 else args[0]
    message = None if args is None or len(args) < 2 else args[1:]
    if trigger is None or message is None:
        connection.notice(event.source.nick, "Please specify a trigger and message.")
        return

    if trigger in bot.storage[key]:
        connection.notice(event.source.nick, "Trigger {0} updated.".format(trigger))
    else:
        connection.notice(event.source.nick, "Trigger {0} added.".format(trigger))

    bot.storage[key][trigger] = " ".join(message)


def can_del(bot, connection, event, args):
    trigger = None if args is None or len(args) == 0 else args[0]
    if trigger is None:
        connection.notice(event.source.nick, "Please specify a trigger.")
        return

    if trigger in bot.storage[key]:
        connection.notice(event.source.nick, "Trigger {0} deleted.".format(trigger))
        del bot.storage[key][trigger]
    else:
        connection.notice(event.source.nick, "Couldn't find trigger {0}.".format(trigger))


def can_list(bot, connection, event, args):
    connection.notice(event.source.nick, "Triggers:")
    for trigger in bot.storage[key].keys():
        connection.notice(event.source.nick, "!{0}: {1}".format(trigger,
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
                        canned responses.")
            return False

        if bot.config.fls.class_id in user['SecondaryClasses'] or \
                user['Level'] >= bot.config.fls.min_level:
                    return True
        else:
            if prompt:
                connection.notice(nick, "You are not authorized to do this command!")
            return False


