"""
Module to allow people to ask to see the core stats of someone through pubmsg or privmsg. This
will display someone's Upload, Download, Ratio, Bonus Points, and link to profile, assuming
that their paranoia is set sufficiently low enough that it is viewable (we don't check to see
if the requesting party has the right permissions to override paranoia if asking in a privmsg)
"""

from hermes.module import event, command


@event("pubmsg")
@command("user", "u")
def show_user(bot, connection, event):
    """
    
    :param bot:
    :type bot: hermes.Hermes
    :param connection: 
    :param event:
    :return: 
    """

    chan = event.target.lstrip('#').lower()

    if chan in bot.config.irc.channels:
        if 'public' in bot.config.irc.channels[chan] and \
                bot.config.irc.channels[chan].public == True:
            return
    else:
        return

    if len(event.args) == 0:
        # We can parse the username off the host string, but only if it's already been set by the
        # bot
        if not event.source.host.endswith(bot.config.site.tld):
            username = event.source.nick
        else:
            username = event.source.host.split(".")[0]
    else:
        username = event.args[0]
    if username is None:
        connection.privmsg(event.target, "No user found with name {}".format(username))
        return
    user = bot.database.get_user(username)
    if user is None or 'DisplayStats' not in user:
        connection.privmsg(event.target, "No user found with name {}".format(username))
        return

    msg = "[ {} ] :: [ {} ] :: [ Uploaded: {} | Downloaded: {} | " \
          "Ratio: {} ] :: [ {} ]".format(user['Username'],
                                         user['ClassName'],
                                         user['DisplayStats']['Uploaded'],
                                         user['DisplayStats']['Downloaded'],
                                         user['DisplayStats']['Ratio'],
                                         user['UserPage'])
    connection.privmsg(event.target, msg)
