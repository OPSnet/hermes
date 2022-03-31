from hermes.module import event as hermes_event, command


BAD_CHARS = set('@!*?')


class WhoisInfo:
    def __init__(self):
        self.nick = None
        self.user = None
        self.vhost = None
        self.ip = None
        self.hostname = None
        self.is_ircop = False

    def incomplete(self):
        return self.nick is None or self.vhost is None

    def process(self, event):
        if event.type == 'whoisuser':
            return self.process_user(event)
        elif event.type == '378':
            return self.process_remote(event)
        raise Exception("unknown whois event")

    def process_user(self, event):
        self.nick, self.user, self.vhost = event.arguments[:3]

    def process_remote(self, event):
        msg = event.arguments[1]
        if not msg.startswith('is connecting from '):
            return
        # msg should be "is connecting from *@hostname ip"
        info = msg.split('@', maxsplit=1)[-1]
        self.hostname, self.ip = info.split(' ')

    def __str__(self):
        if self.is_ircop:
            return f"{self.nick} is an IRCOP"
        return f"{self.nick}!{self.user}@{self.vhost} is connecting from {self.ip} {self.hostname}"


class WhoisCallbackManager:
    TIMEOUT_SECONDS = 15

    def __init__(self, bot, connection, event, user):
        self.bot = bot
        self.conn = connection
        self.event = event
        self.user_nick = self.event.source.nick
        self.user = user  # gazelle user dict for user_nick
        self.whois_nick = event.args[0]
        self.response = WhoisInfo()
        self.is_done = False

    def go(self):
        self._setup_callbacks()
        self.conn.whois([self.whois_nick])

    def _setup_callbacks(self):
        # "<nick> <user> <host> * :<real name>"
        self.conn.add_global_handler('whoisuser', self._collect_whois, 100)
        # 378 is an extension used by unrealircd but not implemented by the irc lib
        # "<nick> <server> :is connecting from *@<hostname> <ip>"
        self.conn.add_global_handler('378', self._collect_whois, 100)
        # "<nick> :is an IRC operator"
        self.conn.add_global_handler('whoisoperator', self._abort_whois, 100)
        # done
        self.conn.add_global_handler('endofwhois', self._finish_whois, 100)
        self.conn.reactor.scheduler.execute_after(self.TIMEOUT_SECONDS, self._timeout)

    def _timeout(self):
        if self.is_done:
            return
        self.conn.notice(self.user_nick, f"whois for {self.whois_nick} timed out")
        self._remove_handlers(self.conn)

    def _check_event(self, event):
        if self.is_done or len(event.arguments) < 1:
            return False
        return event.arguments[0] == self.whois_nick

    def _abort_whois(self, connection, event):
        if not self._check_event(event):
            return
        self.is_done = True
        self.response.is_ircop = True
        self._remove_handlers(connection)
        connection.notice(self.user_nick, f"{self.whois_nick} is an IRCOP")

    def _collect_whois(self, connection, event):
        if not self._check_event(event):
            return
        self.response.process(event)

    def _finish_whois(self, connection, event):
        if not self._check_event(event):
            return
        self.is_done = True
        self._remove_handlers(connection)
        if self._check_permissions():
            if self.response.incomplete():
                connection.privmsg(self.user_nick, "user not found")
            else:
                connection.privmsg(self.user_nick, str(self.response))
        else:
            connection.privmsg(self.user_nick, "not allowed to whois this user")

    def _remove_handlers(self, connection):
        connection.remove_global_handler('whoisuser', self._collect_whois)
        connection.remove_global_handler('378', self._collect_whois)
        connection.remove_global_handler('whoisoperator', self._abort_whois)
        connection.remove_global_handler('endofwhois', self._finish_whois)

    def _check_permissions(self):
        if self.response.is_ircop:
            # this should never trigger because it enters _abort_whois()
            return False
        if self.response.incomplete():
            return True
        if self.response.vhost.endswith(self.bot.config.site.tld):
            # authenicated users are protected
            return False
        return True


async def check_auth(bot, host, target_user):
    split_host = host.split('.')
    if len(split_host) != 4 or not host.endswith(bot.config.site.tld):
        return False

    user = await bot.api.get_user(split_host[0])
    if user is None:
        return False

    if user['Level'] >= bot.config.site.mod_level:
        return user

    if bot.config.interview.class_id in user['SecondaryClasses']:
        for chan in [bot.config.interview.main_channel] + bot.config.interview.channels:
            irc_chan = bot.channels.get('#' + chan)
            if irc_chan and irc_chan.has_user(target_user):
                return user

    return False


@hermes_event('privmsg')
@command('whois')
async def whois(bot, connection, event):
    if len(event.args) != 1:
        connection.privmsg(event.target, "{} <nick>".format(event.cmd))
        return

    target = event.args[0]
    if not BAD_CHARS.isdisjoint(target):
        connection.notice(event.source.nick, "can only whois usernames")
        return

    user = await check_auth(bot, event.source.host, target)
    if not user:
        connection.notice(event.source.nick, "not allowed to whois this user")
        return

    mgr = WhoisCallbackManager(bot, connection, event, user)
    mgr.go()
