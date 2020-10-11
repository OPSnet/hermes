"""
This module parses any youtube link posted in privmsg or pubmsg, responding (either in the
privmsg or to the channel the link was posted on) with the name of the video, how many views it
has gotten and then the link. Useful as most members don't like to have to click on links to
see what it actually is.
"""

import locale
import re

import requests
from hermes.module import event, rule, disabled


@disabled()
@rule(r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?[\w\?=]*)?",
      re.IGNORECASE)
@event("privmsg", "pubmsg")
def parse_youtube(bot, connection, event, match):
    """

    :param bot:
    :type bot: hermes.Hermes
    :param connection:
    :param event:
    :param match:
    :return:
    """
    if not hasattr(bot.config, "youtube_api"):
        return
    if event.type == "privmsg":
        target = event.source.nick
    else:
        target = event.target

    video_id = match.group(1)
    params = {'key': bot.config.youtube_api, 'id': video_id, 'maxResults': 1,
              'part': 'id,snippet,statistics'}
    req = requests.get("https://www.googleapis.com/youtube/v3/videos/", params)
    payload = req.json()
    if payload['pageInfo']['totalResults'] == 0:
        return "Youtube video not found!"
    video = payload['items'][0]
    title = str(video['snippet']['title'])
    views = locale.format("%d", int(video['statistics']['viewCount']), grouping=True)
    msg = "[ {} | {} views | https://www.youtube.com/watch?v={} ]".format(title, views, video_id)
    connection.privmsg(target, msg)
