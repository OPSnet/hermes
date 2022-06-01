import threading
import irc.bot
import irc.client
from datetime import datetime, timedelta


class ServerConnection(irc.client.ServerConnection):
    def __init__(self, reactor):
        super(ServerConnection, self).__init__(reactor)
        self.last_ping = None
        self.last_pong = None
        self._write_mutex = threading.Lock()

    def ping(self, target, target2=""):
        """Send a PING command."""
        if not self.is_connected():
            return
        self.last_ping = datetime.now()
        self.send_items('PING', target, target2)

    def kill(self, nick, comment=""):
        """Send a KILL command."""
        self.send_items('KILL', nick, comment and ':' + comment)

    def send_raw(self, string):
        with self._write_mutex:
            super().send_raw(string)


class Reactor(irc.client.Reactor):
    connection_class = ServerConnection


class IRCBot(irc.bot.SingleServerIRCBot):
    reactor_class = Reactor
    timeout_interval = 40
    check_keepalive_interval = 20
    keepalive_interval = 10

    def __init__(
        self,
        server_list,
        nickname,
        realname,
        recon=None,
        **connect_params
    ):
        if recon is None:
            recon = irc.bot.ExponentialBackoff(min_interval=10, max_interval=300)

        super(IRCBot, self).__init__(
            server_list,
            nickname,
            realname,
            irc.bot.missing,
            recon,
            **connect_params
        )

        for i in ['welcome', 'pong']:
            self.connection.add_global_handler(i, getattr(self, '_on_' + i), -20)

        self.reactor.scheduler.execute_every(
            timedelta(seconds=self.check_keepalive_interval),
            self.check_keepalive
        )

    def check_keepalive(self):
        if self.connection.last_pong is None or not self.connection.is_connected():
            return
        timeout = self.connection.last_pong + timedelta(seconds=self.timeout_interval)
        if self.connection.last_ping > timeout:
            self.connection.last_pong = None
            self.disconnect('disconnecting...')

    def _on_welcome(self, connection, event):
        period = timedelta(seconds=self.keepalive_interval)
        connection.set_keepalive(period)

    def _on_pong(self, connection, event):
        self.connection.last_pong = datetime.now()
