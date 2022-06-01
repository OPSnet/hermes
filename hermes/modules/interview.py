"""
Module to handle interview queues
"""

from hermes.module import event, command
from time import time
import re

key = 'interview_queue'
speedtest_key = 'speedtest_history'


def setup(bot):
    if bot.storage[key] is None:
        bot.storage[key] = list()
    if bot.storage[speedtest_key] is None:
        bot.storage[speedtest_key] = list()


def convert_time(diff):
    seconds = diff % 60
    diff = (diff - seconds) / 60
    minutes = diff % 60
    diff = (diff - minutes) / 60
    hours = diff % 24
    days = (diff - hours) / 24
    return days, hours, minutes, seconds


class UserClass:
    def __init__(self, nick, host, user, speed_test):
        self.nick = nick
        self.host = host
        self.user = user
        self.time = time()
        self.speed_test = speed_test
        self.postponed = False

    def get_waited(self):
        waited = time() - self.time
        return convert_time(waited)

    def get_waited_str(self):
        days, hours, minutes, seconds = self.get_waited()
        return "{} days, {} hours, {} minutes, and " \
               "{} seconds".format(str(round(days)), str(round(hours)), str(round(minutes)),
                                    str(round(seconds)))

    def get_full_name(self):
        return "{}!{}@{}".format(self.nick, self.user, self.host)


def is_in_queue(bot, user, host):
    is_already_in_queue = False
    position = 0
    for i in range(len(bot.storage[key])):
        if user == bot.storage[key][i].user and host == bot.storage[key][i].host:
            is_already_in_queue = True
            position = i
    return is_already_in_queue, position


def is_url_reused(bot, url):
    return url in bot.storage[speedtest_key]


async def check_auth(bot, connection, host, nick, prompt):
    split_host = host.split(".")
    if len(split_host) != 4:
        return False

    if host.endswith(bot.config.site.tld):
        # Make sure that the one issuing the command is authorized to do so
        user = await bot.api.get_user(split_host[0])
        if user is None:
            if prompt:
                connection.notice(nick, "You must be authed through the bot to start an interview.")
            return False

        if bot.config.interview.class_id in user['SecondaryClasses'] or \
                user['Level'] >= bot.config.interview.min_level:
            return True
        else:
            if prompt:
                connection.notice(nick, "You are not authorized to do this command!")
            return False


def is_in_channel(user, channel):
    for chan_user in channel.users():
        if user.nick.lower() == chan_user.lower():
            return True
    return False


def next_user(bot, connection):
    while len(bot.storage[key]) > 0:
        user = bot.storage[key].pop(0)
        if is_in_channel(user, bot.channels['#recruitment']):
            return user
    return None


@event("privmsg")
@command("queue")
async def queue(bot, connection, event):
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

    if await check_auth(bot, connection, host, nick, False):
        if len(bot.storage[key]) == 0:
            connection.notice(nick, "The queue is empty")
        else:
            connection.notice(nick, "The queue currently has {} people in it:".format(len(bot.storage[key])))
            for x in range(len(bot.storage[key])):
                person = bot.storage[key][x]
                connection.notice(nick, "{}) {} - {}".format(x+1, person.nick, person.get_waited_str()))
    else:
        if len(event.args) == 0:
            connection.notice(nick, "The queue command requires a speedtest URL.")
            return

        speed_test = event.args[0]

        if 'speedtest_urls' in bot.config.interview and isinstance(bot.config.interview.speedtest_urls,
                                                                   list):
            match = next(re.match(regex, speed_test) for regex in bot.config.interview.speedtest_urls)
            if match:
                if len(match.groups()) > 0:
                    speed_test = "https://www.speedtest.net/result/{0}.png".format(match.group(1))
            else:
                connection.notice(nick, "Speedtest URL must be directly to the image, refer to "
                                        "Starting the Interview at {} if you are "
                                        "unsure.".format(bot.config.interview.site))
                return

        is_already_in_queue, position = is_in_queue(bot, user, host)
        if is_already_in_queue:
            connection.notice(nick, "You are already in the queue at position "
                                    "{}.".format(str(position + 1)))
        else:
            if is_url_reused(bot, speed_test):
                connection.notice(nick, "Speedtest URL has already been used, take another")
                return

            bot.storage[speedtest_key].append(speed_test)
            bot.storage[key].append(UserClass(nick, host, user, speed_test))
            connection.notice(nick, "Successfully added to queue. You are at position "
                                    "{}.".format(str(len(bot.storage[key]))))
            bot.logger.debug("Successfully queued {} at {}.".format(nick, str(len(bot.storage[key]))))


@event("privmsg")
@command("info")
def info(bot, connection, event):
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

    is_already_in_queue, position = is_in_queue(bot, user, host)
    if is_already_in_queue:
        connection.notice(nick, "You are in the queue at position {}.".format(str(position + 1)))
        connection.notice(nick, "You have waited for {}.".format(bot.storage[key][position].get_waited_str()))
    else:
        connection.notice(nick, "You are not in the queue. To enter it type "
                                "!queue <speedtest URL>.")


@event("privmsg", "pubmsg")
@command("next")
async def next_interview(bot, connection, event):
    """

    :param bot:
    :type bot: hermes.Hermes
    :param connection:
    :param event:
    :return:
    """
    nick = event.source.nick
    host = event.source.host

    if len(event.args) == 0:
        connection.notice(nick, "The next command requires a channel name.")
        return

    chan = event.args[0].lstrip('#')

    if await check_auth(bot, connection, host, nick, True):
        if chan.lower() not in bot.config.interview.channels:
            connection.notice(nick, "Must use an official interview channel: #{}".format(
                ", #".join(bot.config.interview.channels)))
            return

        user = next_user(bot, connection)

        if not user:
            connection.notice(nick, "Cannot perform command, queue is empty.")
        else:
            connection.notice(nick, "Next candidate is {}. Speedtest URL is "
                                    "{}.".format(user.get_full_name(), user.speed_test))
            connection.send_raw("SAJOIN {} #{}".format(user.nick, chan))
            connection.privmsg(user.nick, "You have been have been invited to take your "
                                               "interview in #{}.".format(chan))


@event("privmsg")
@command("queue_length")
def queue_length(bot, connection, event):
    connection.notice(event.source.nick, "The queue currently has {} people "
                                         "in it.".format(len(bot.storage[key])))


@event("privmsg")
@command("postpone")
def postpone(bot, connection, event):
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

    is_already_in_queue, position = is_in_queue(bot, user, host)
    if is_already_in_queue:
        if position + 1 == len(bot.storage[key]):
            connection.notice(nick, "You are already at the end of the queue.")
        else:
            user = bot.storage[key].pop(position)
            bot.storage[key].insert(position + 1, user)
            connection.notice(nick, "You are now in the queue at position "
                                    "{}.".format(str(position + 2)))
    else:
        connection.notice(nick, "You are not in the queue. To enter it type "
                                "!queue <speedtest URL>.")


@event("privmsg")
@command("cancel")
def cancel(bot, connection, event):
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

    is_already_in_queue, position = is_in_queue(bot, user, host)
    if is_already_in_queue:
        bot.storage[key].pop(position)
        connection.notice(nick, "Successfully removed you from the queue.")
    else:
        connection.notice(nick, "You have not been added to the queue. To enter it type "
                                "!queue <speedtest URL>.")
