import irc.client
import irc.bot
import pytest
from unittest.mock import MagicMock

from hermes.modules import disabled
from hermes.utils import convert


class Event(irc.client.Event):
    @property
    def args(self):
        args = self.arguments[0].split()
        return args[1:] if len(args) > 1 else []

    @property
    def cmd(self):
        return self.arguments[0].lower()


@pytest.fixture
def irc_bot():
    bot = irc.bot.SingleServerIRCBot(
        server_list=[('localhost', '9999')],
        realname='irclibbot',
        nickname='irclibbot',
    )
    channel = irc.bot.Channel()
    channel.add_user('someuser')
    bot.channels['#disabled'] = channel
    channel = irc.bot.Channel()
    channel.add_user('interviewuser')
    bot.channels['#disabled-1'] = channel
    bot.config = convert({'site': {'tld': 'example.test'}})
    bot.connection.send_raw = MagicMock()
    bot.connection.send_items = MagicMock()
    bot.connection.kick = MagicMock()
    yield bot


def test_disabled_move_success(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled',
        arguments=['.disabled-move someuser 1']
    )
    disabled.disabled_move(irc_bot, irc_bot.connection, event)
    irc_bot.connection.send_items.assert_called_once()
    call = irc_bot.connection.send_items.call_args
    assert call.args[0] == 'SAJOIN'


def test_disabled_move_nouser(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled',
        arguments=['.disabled-move notinterviewuser 1']
    )
    disabled.disabled_move(irc_bot, irc_bot.connection, event)
    irc_bot.connection.kick.assert_not_called()
    irc_bot.connection.send_items.assert_called_once()
    call = irc_bot.connection.send_items.call_args
    assert call.args[0] == 'PRIVMSG'


def test_disabled_kick_success(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled',
        arguments=['.disabled-kick interviewuser 1']
    )
    disabled.disabled_kick(irc_bot, irc_bot.connection, event)
    irc_bot.connection.kick.assert_called_once()
    call = irc_bot.connection.kick.call_args
    assert call.args[1] == 'interviewuser'


def test_disabled_kick_nouser(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled',
        arguments=['.disabled-kick notinterviewuser 1']
    )
    disabled.disabled_kick(irc_bot, irc_bot.connection, event)
    irc_bot.connection.kick.assert_not_called()
    irc_bot.connection.send_items.assert_called_once()
    call = irc_bot.connection.send_items.call_args
    assert call.args[0] == 'PRIVMSG'


def test_process_arguments_unprivileged(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.User.example.test'),
        target='#disabled',
        arguments=['.disabled-move someuser 1']
    )
    with pytest.raises(disabled.BadCommand):
        disabled.process_arguments(irc_bot, irc_bot.connection, event)


def test_process_arguments_implicit_channel(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled-1',
        arguments=['.disabled-move someuser']
    )
    result = disabled.process_arguments(irc_bot, irc_bot.connection, event)
    assert result[1] == '#disabled-1'


def test_process_arguments_bad_channel(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled',
        arguments=['.disabled-move someuser nope']
    )
    with pytest.raises(disabled.BadCommand):
        disabled.process_arguments(irc_bot, irc_bot.connection, event)


def test_process_arguments_bad_channel2(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled',
        arguments=['.disabled-move someuser -1']
    )
    with pytest.raises(disabled.BadCommand):
        disabled.process_arguments(irc_bot, irc_bot.connection, event)


def test_process_arguments_no_channel(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled',
        arguments=['.disabled-move someuser']
    )
    with pytest.raises(disabled.BadCommand):
        disabled.process_arguments(irc_bot, irc_bot.connection, event)


def test_process_arguments_no_nick(irc_bot):
    event = Event(
        type='privmsg',
        source=irc.client.NickMask('nick!userid@name.Moderator.example.test'),
        target='#disabled',
        arguments=['.disabled-move']
    )
    with pytest.raises(disabled.BadCommand):
        disabled.process_arguments(irc_bot, irc_bot.connection, event)
