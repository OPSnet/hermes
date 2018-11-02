"""
Module to administrate the cache
"""

from hermes.module import event, command, admin_only

@event('privmsg')
@command('cache')
@admin_only()
def cache_control(bot, connection, event):
    if len(event.args) < 1:
        pass
    nick = event.source.nick
    command = event.args[0]
    if command == 'clear':
        if len(event.args) == 1:
            bot.cache.clear()
            connection.privmsg(nick, "Cache cleared")
        else:
            for key in event.args[1:]:
                bot.cache.clear(key)
            connection.privmsg(nick, "Cleared cache keys {0}".format(", ".join(event.args[1:])))
    elif command == 'count':
        connection.privmsg(nick, "Cache keys: {0}".format(str(len(bot.cache))))
    elif command == 'expire':
        bot.cache.expire()
        connection.privmsg(nick, "Expired cache keys purged")

