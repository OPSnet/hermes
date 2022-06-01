from re import IGNORECASE
from hermes.module import rule, event, disabled

def check_perms(bot, channel, level):
    channel = channel.lstrip('#').lower()
    if channel not in bot.config.irc.channels:
        return False
    config_channel = bot.config.irc.channels[channel]
    if 'min_level' not in config_channel or level > config_channel.min_level or (
            'public' in config_channel and config_channel.public == True):
                return False

    return True

@event("pubmsg")
@rule(r"https:\/\/orpheus\.network\/forums\.php\?[a-zA-Z0-9=&]*threadid=([0-9]+)", IGNORECASE)
async def parse_thread_url(bot, connection, event, match):
    """

    :param bot:
    :type bot: hermes.Hermes
    :param connection:
    :param event:
    :param match:
    :return:
    """
    topic = await bot.api.get_topic(int(match.group(1)))
    if topic is not None:
        if not check_perms(bot, event.target, topic.MinClassRead):
            return

        msg = "[ Forums :: {0} | {1} ]".format(topic.Forum, topic.Title)
        connection.privmsg(event.target, msg)


@event("pubmsg")
@rule(r"https:\/\/orpheus\.network\/wiki\.php\?[a-zA-Z0-9=&]*id=([0-9]+)")
async def parse_wiki_url(bot, connection, event, match):
    wiki = await bot.api.get_wiki(int(match.group(1)))
    if wiki is not None:
        if not check_perms(bot, event.target, wiki.MinClassRead):
            return

        msg = "[ Wiki :: {0} ]".format(wiki.Title)
        connection.privmsg(event.target, msg)


@event("pubmsg")
@rule(r"https:\/\/orpheus\.network\/user\.php\?[a-zA-Z0-9=&]*id=([0-9]+)")
async def parse_user_url(bot, connection, event, match):
    user = await bot.api.get_user(int(match.group(1)))
    if user is not None:
        msg = "[ {0} ] :: [ {1} ] :: [ Uploaded: {2} | Downloaded: {3} | " \
              "Ratio: {4} ]".format(user.Username, user.ClassName, user.DisplayStats.Uploaded,
                                    user.DisplayStats.Downloaded, user.DisplayStats.Ratio)
        connection.privmsg(event.target, msg)


@event("pubmsg")
@rule(r"https:\/\/orpheus\.network\/requests\.php\?[a-zA-Z0-9=&]*id=([0-9]+)")
async def parse_request_url(bot, connection, event, match):
    request = await bot.api.get_request(int(match.group(1)))
    if request is not None:
        msg = "[ Request :: {0} - {1} ({2}) ]".format(request.DisplayArtists, request.Title,
                request.Year)
        connection.privmsg(event.target, msg)


@event("pubmsg")
@rule(r"https:\/\/orpheus\.network\/torrents\.php\?[a-zA-Z0-9=&]*torrentid=([0-9]+)")
async def parse_torrent_url(bot, connection, event, match):
    torrent = await bot.api.get_torrent(int(match.group(1)))
    if torrent is not None:
        if torrent.HasLogDB == "1":
            log = " {0}%".format(torrent.LogScore)
        elif torrent.HasLog == "1":
            log = " Log"
        else:
            log = ""

        msg = "[ Torrent :: {0} - {1} ({2}) [{3}] | {4} {5}{6} ]".format(torrent.DisplayArtists,
                torrent.Name, torrent.Year, torrent.ReleaseType, torrent.Media, torrent.Format,
                log)
        connection.privmsg(event.target, msg)


@event("pubmsg")
@rule(r"https:\/\/orpheus\.network\/torrents\.php[a-zA-Z0-9=&\?]*[\?&]id=([0-9]+)$")
async def parse_torrent_group_url(bot, connection, event, match):
    group = await bot.api.get_torrent_group(int(match.group(1)))
    if group is not None:
        msg = "[ Torrent :: {0} - {1} ({2}) [{3}] ]".format(group.DisplayArtists, group.Name,
                group.Year, group.ReleaseType)
        connection.privmsg(event.target, msg)


@event("pubmsg")
@rule(r"https:\/\/orpheus\.network\/artist\.php\?[a-zA-Z0-9=&]*id=([0-9]+)")
async def parse_artist_url(bot, connection, event, match):
    artist = await bot.api.get_artist(int(match.group(1)))
    if artist is not None:
        msg = "[ Artist :: {0} ]".format(artist.Name)
        connection.privmsg(event.target, msg)


@event("pubmsg")
@rule(r"https:\/\/orpheus\.network\/collages\.php\?[a-zA-Z0-9=&]*id=([0-9]+)")
async def parse_collage_url(bot, connection, event, match):
    collage = await bot.api.get_collage(int(match.group(1)))
    if collage is not None:
        msg = "[ Collage :: {0} [{1}] ]".format(collage.Name, collage.Category)
        connection.privmsg(event.target, msg)
