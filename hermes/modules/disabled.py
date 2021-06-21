from hermes.module import event, command
MAIN_CHANNEL = '#disabled'
INTERVIEW_CHANNEL_MAXID = 5
INTERVIEW_CHANNEL_FMT = '#disabled-{chanid}'
INTERVIEW_CHANNELS = {INTERVIEW_CHANNEL_FMT.format(chanid=chan_id)
                      for chan_id in range(1, INTERVIEW_CHANNEL_MAXID + 1)}
ALLOWED_USER_CLASSES = {'Moderator', 'SeniorModerator', 'LeadDeveloper'}


class BadCommand(Exception):
    pass


def check_auth(bot, host):
    split_host = host.split('.')
    if len(split_host) == 3 and split_host[0] == 'sysop' \
            and host.endswith(bot.config.site.tld):
        return True
    if len(split_host) != 4:
        return False

    user_class = split_host[1]
    return host.endswith(bot.config.site.tld) \
        and user_class in ALLOWED_USER_CLASSES


def process_arguments(bot, connection, event):
    if not check_auth(bot, event.source.host):
        connection.privmsg(event.target,
                           "You are not authorized to do this command!")
        raise BadCommand()

    if len(event.args) > 0:
        target_user = event.args[0]
    else:
        connection.privmsg(event.target, "{} <nick> [<chanid>]".format(event.cmd))
        raise BadCommand()

    if len(event.args) >= 2:
        target_id = event.args[1]
        target_chan = INTERVIEW_CHANNEL_FMT.format(chanid=target_id)
        if target_chan not in INTERVIEW_CHANNELS:
            connection.privmsg(event.target, "invalid chanid")
            raise BadCommand()
    elif event.target in INTERVIEW_CHANNELS:
        target_chan = event.target
    else:
        connection.privmsg(event.target, "no chanid")
        raise BadCommand()

    return target_user, target_chan


@event('privmsg', 'pubmsg')
@command('disabled-move')
def disabled_move(bot, connection, event):
    try:
        target_user, target_chan = process_arguments(bot, connection, event)
    except BadCommand:
        return

    if not bot.channels[MAIN_CHANNEL].has_user(target_user):
        connection.privmsg(event.target, "user not in {}".format(MAIN_CHANNEL))
        return

    connection.send_items('SAJOIN', target_user, target_chan)


@event('privmsg', 'pubmsg')
@command('disabled-kick')
def disabled_kick(bot, connection, event):
    try:
        target_user, target_chan = process_arguments(bot, connection, event)
    except BadCommand:
        return

    if not bot.channels[target_chan].has_user(target_user):
        connection.privmsg(event.target, "user not in channel")
        return

    connection.kick(target_chan, target_user)
