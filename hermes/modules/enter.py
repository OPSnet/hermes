"""
Module that allows good-standing members (don't have IRC privileges revoked) to enter the
official IRC channels (which should all be +i and not regularly joinable), as well as to have
their ident and host be changed such that they'll be <user_id>@<user_name>.<group_name>.<site_tld>
which allows for better anonymization than default IRC.

Note, because the bot is using SAJOIN to add users to the channels that they request to enter,
we cannot use a +b ban on a user to prevent them from joining a channel. Instead, we have to
revoke their IRC privileges through Gazelle, then kick the user from the channels.
"""
import re
from datetime import timedelta
from hermes.module import privmsg, command, help_message, example


def validate_irckey(user, irckey):
    if user == None:
        return False, "No user found with that name."
    else:
        if user.Enabled != '1' or user.DisableIRC == '1':
            return False, "Your IRC privileges have been disabled. Join #disabled."
        elif user.IRCKey == irckey:
            return True, ""
        else:
            return False, "Invalid Username/IRC Key"

@privmsg()
@command("enter")
@help_message("Use this command to have the bot add you to any official channel")
@example("enter <site_username> <site_irckey> <channels>",
         "enter #APOLLO itismadness 123456",
         "enter #APOLLO #announce itismadness 123456",
         "enter #APOLLO,#announce itismadness 123456")
def enter(bot, connection, event):
    """
    
    :param bot: 
    :type bot: hermes.Hermes
    :param connection: 
    :param event: 
    :return: 
    """

    sent_nick = event.source.nick
    if len(event.args) < 3:
        connection.privmsg(sent_nick, "Not enough arguments for enter command")
        connection.privmsg(sent_nick, "enter <channels> <username> <password>")
        return
    username = event.args[-2]
    password = event.args[-1]
    channels = []
    for channel in event.args[:-2]:
        channels.extend([chan.strip() for chan in channel.strip().split(",")])
    bot.logger.debug("-> {} (username: {}) wants to enter {}".format(sent_nick, username,
                                                                     ", ".join(channels)))

    # Pull fresh copy of user, use the cached version if no user is found
    key = "user_{0}".format(username)
    user = bot.database.get_user(username)
    if user == None:
        user = bot.cache[key]
    valid, error = validate_irckey(user, password)

    if valid:
        bot.cache.store(key, user, timedelta(30))
        connection.send_raw("CHGIDENT {} {}".format(sent_nick, user.ID))
        connection.send_raw("CHGHOST {} {}.{}.{}".format(sent_nick, user.Username,
                                                         user.ClassName.replace(" ", ""),
                                                         bot.config.site.tld))
        joined = []
        not_real = []
        not_joined = []
        for channel in channels:
            channel = channel.lstrip('#')
            real_channel = None
            for bot_channel in bot.config.irc.channels:
                if channel.lower() == bot_channel.lower():
                    real_channel = bot_channel
                    break

            # Is this a channel the bot is actively watching and cares about?
            if real_channel is not None:
                join_channel = True
                # Does the channel have a minimum level set and does the user's class exceed it?
                if 'min_level' in bot.config.irc.channels[real_channel]:
                    if bot.config.irc.channels[real_channel].min_level > int(user.Level):
                        join_channel = False
                # Does the channel allow certain classes in the channel and does the user
                # have that class as either the primary class or one of his secondary classes?
                if not join_channel and 'classes' in bot.config.irc.channels[real_channel]:
                    # get intersection of the user's primary class, secondary classes, and classes
                    # that are allowed for the channel
                    intersect = set(user.SecondaryClasses + [user.Class]) & \
                                set(bot.config.irc.channels[real_channel].classes)
                    if len(intersect) > 0:
                        join_channel = True
                if join_channel:
                    joined.append(real_channel)
                    connection.send_raw("SAJOIN {} #{}".format(sent_nick, real_channel))
                else:
                    not_joined.append(channel)
            else:
                not_real.append(channel)

        if len(not_real) > 0:
            connection.privmsg(sent_nick,
                               "I'm sorry, the channels #{} do not "
                               "exist".format(", #".join(not_real)))

        if len(not_joined) > 0:
            connection.privmsg(sent_nick,
                               "I'm sorry, you lack the right permissions to "
                               "join #{}".format(", #".join(not_joined)))

        if len(joined) > 0:
            connection.privmsg(sent_nick, "Welcome to #{}".format(", #".join(joined)))
            bot.logger.debug("-> {} entered #{}".format(sent_nick, ", #".join(joined)))
    else:
        connection.privmsg(sent_nick, error)
