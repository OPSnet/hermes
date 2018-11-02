from re import IGNORECASE
from hermes.module import rule, event, disabled


@disabled()
@event("privmsg", "pubmsg")
@rule(r"(https|http):\/\/(apollo|xanax)\.rip\/forums\.php\?([a-zA-Z0-9=&]*)threadid=([0-9]+)",
      IGNORECASE)
def parse_thread_url(bot, connection, event, match):
    """
    
    :param bot: 
    :type bot: hermes.Hermes
    :param connection: 
    :param event: 
    :param match: 
    :return: 
    """
    topic = bot.database.get_topic(int(match.group(4)))
    if event.type == "privmsg":
        target = event.source.nick
    else:
        target = event.target
    if topic is None:
        msg = "Could not find topic"
    else:
        msg = "[ {} | " \
              "https://apollo.rip/forums.php?action=showthread&threadid={} ]".format(topic.title,
                                                                                     topic.id)
    connection.privmsg(target, msg)
