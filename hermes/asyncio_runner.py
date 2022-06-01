"""
This whole thing is a hack to run commands asynchronously, stopping them
from blocking the main thread (api requests!).

Ideally we switch over to irc.aio_client some time.
"""

import asyncio
import threading
import logging
import re

logger = logging.getLogger(__name__)


class ModuleRunner(threading.Thread):
    TIMEOUT = 120  # module call timeout in seconds

    def __init__(self, bot, *a, **kw):
        super().__init__(*a, **kw, daemon=True)
        self.bot = bot
        self._loop = None

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def stop(self):
        if not self._loop:
            return
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._loop = None

    def queue(self, name, func, connection, event):
        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(
            self._execute_module(name, func, connection, event), self._loop)

    async def _execute_module(self, name, func, connection, event):
        # noinspection PyBroadException
        try:
            await asyncio.wait_for(
                self._execute_function(func, connection, event), self.TIMEOUT)
        except asyncio.TimeoutError:
            logger.warning(f"Failed to run function: {name}.{func.__name__}"
                           f" - timeout")
        except Exception:
            if event.type == "privmsg":
                msg = f"I'm sorry, {name}.{func.__name__} threw an exception."\
                      " Please tell an administrator and try again later."
                connection.privmsg(event.source.nick, msg)
            logger.exception(f"Failed to run function: {name}.{func.__name__}")

    async def _execute_function(self, func, connection, event):
        cmd = event.cmd
        if hasattr(func, "commands"):
            for command in func.commands:
                if cmd == "." + command or cmd == "!" + command or \
                        (event.type == "privmsg" and cmd == command):
                    result = func(self.bot, connection, event)
                    if asyncio.iscoroutine(result):
                        await result
        if hasattr(func, "rules"):
            for rule in func.rules:
                match = re.search(rule, event.msg)
                if match:
                    result = func(self.bot, connection, event, match)
                    if asyncio.iscoroutine(result):
                        await result
