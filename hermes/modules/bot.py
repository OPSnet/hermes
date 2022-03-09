"""
Module for governing certain admin commands for the bot such as restarting it, updating it (via
git), killing the bot, and printing out its version.
"""
import os
import sys

from hermes.hermes import get_version_string
from hermes.module import admin_only, privmsg, command
from hermes.utils import run_popen, file_tail


@admin_only()
@privmsg()
@command("restart")
def restart_bot(bot, connection, event):
    connection.privmsg(event.source.nick, "Saving persistent data")
    bot.logger.info("-> Saving data")
    bot.storage.save()
    connection.privmsg(event.source.nick, "Restarting the bot now")
    bot.logger.info("-> Restarting bot")
    pidfile = os.path.join(bot.dir, "hermes.pid")
    if os.path.isfile(pidfile):
        os.unlink(pidfile)
    os.execl(sys.executable, *([sys.executable] + sys.argv))


@admin_only()
@privmsg()
@command('restart_socket')
def restart_socket(bot, connection, event):
    if bot.listener is not None:
        connection.privmsg(event.source.nick, 'Restarting the socket')
        bot.listener.restart = True
    else:
        connection.privmsg(event.source.nick, 'Not using socket')


@admin_only()
@privmsg()
@command("update")
def update_bot(bot, connection, event):

    git_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

    if os.path.isdir(os.path.join(git_dir, ".git")):
        current_dir = os.getcwd()
        os.chdir(git_dir)
        get_version(bot, connection, event)
        out, err = run_popen("git pull")
        connection.privmsg(event.source.nick, "Running git pull...")
        bot.logger.info("-> Updating bot, running git pull")
        bot.logger.info(str(out, "utf-8"))
        if err is not None and str(err, "utf-8") != "":
            bot.logger.error(str(err, "utf-8"))
        os.chdir(current_dir)
        get_version(bot, connection, event)
        # restart_bot(bot, connection, event)
    else:
        connection.privmsg(
            event.source.nick,
            "Can only update bot if run from git directory."
        )


@admin_only()
@privmsg()
@command("kill")
def kill_bot(bot, *_):
    bot.logger.info("-> Killing bot")
    raise SystemExit


@admin_only()
@privmsg()
@command("version")
def get_version(_, connection, event):
    connection.privmsg(
        event.source.nick,
        "Running version: {}".format(get_version_string())
    )


@admin_only()
@privmsg()
@command('view_log')
def view_log(bot, connection, event):
    log_file = os.path.join(bot.dir, 'hermes.log')
    try:
        connection.privmsg(event.source.nick, "Log file: {}".format(log_file))
        for line in file_tail(log_file, 30):
            connection.privmsg(event.source.nick, line.strip())
    except Exception as e:
        connection.privmsg(event.source.nick, e)


@admin_only()
@privmsg()
@command("resetpolls")
def reset_polls(bot, connection, event):
    bot.api_poll_results = []
    bot.api_poll_messaged = False
    connection.privmsg(event.source.nick, "Reset API polling service.")
