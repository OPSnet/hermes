import logging
import threading
from datetime import datetime
import irc.client
from .utils import pretty_time_delta
from flask import Flask, request, abort


logger = logging.getLogger(__name__)
app = Flask('hermes HTTP listener')


@app.route('/irc_msg/<target>', methods=('POST',))
def irc_msg(target):
    """
    :param target: channel/user to send privmsg to
    :param request body: msg to send
    """
    logger.debug(f"received irc_msg for '{target}': '{request.data}'")
    if not target or target == '#' or request.content_length < 1:
        abort(400)
    msg = request.data.decode('utf-8', errors='replace').strip()
    try:
        app.config['irc_connection'].privmsg(target, msg)
    except irc.client.MessageTooLong:
        logger.warning(f"-> Skipping input as too long: {msg}")
        abort(500)
    except irc.client.InvalidCharacters:
        logger.warning(f"-> Skipping message as contained newlines: {msg}")
        abort(500)
    return 'success'


@app.route('/alert', methods=('POST',))
def irc_alert():
    """
    handles alertmanager webhook alerts

    {
      "version": "4",
      "groupKey": <string>,              // key identifying the group of alerts (e.g. to deduplicate)
      "truncatedAlerts": <int>,          // how many alerts have been truncated due to "max_alerts"
      "status": "<resolved|firing>",
      "receiver": <string>,
      "groupLabels": <object>,
      "commonLabels": <object>,
      "commonAnnotations": <object>,
      "externalURL": <string>,           // backlink to the Alertmanager.
      "alerts": [
        {
          "status": "<resolved|firing>",
          "labels": <object>,
          "annotations": <object>,
          "startsAt": "<rfc3339>",
          "endsAt": "<rfc3339>",
          "generatorURL": <string>,      // identifies the entity that caused the alert
          "fingerprint": <string>        // fingerprint to identify the alert
        },
        ...
      ]
    }
    """
    if 'alert_channel' not in app.config:
        abort(503)
    data = request.get_json()
    errors = 0
    now = datetime.utcnow()
    for alert in data['alerts']:
        try:
            start = datetime.fromisoformat(alert['startsAt'][:23])
            duration = now - start
            duration_str = pretty_time_delta(duration.seconds)
            name = alert['labels'].pop('alertname')
            app.config['irc_connection'].privmsg(
                app.config['alert_channel'],
                f"{alert['status']}: {name} {alert['labels']}, "
                f"for {duration_str}"
            )
        except Exception as e:
            app.config['irc_connection'].privmsg(
                app.config['alert_channel'],
                f"failed to send alert: {e}, {alert}"
            )
            errors += 1

    if errors > 0 and errors == len(data['alerts']):
        abort(500)
    return 'success'


class HttpThread(threading.Thread):
    """
    Gazelle communicates with the IRC bot through a socket. Gazelle will send things
    like new torrents (via announce) or reports/errors that the bot would then properly
    relay into the appropriate IRC channels.
    """
    def __init__(self, config):
        self.host = config['host']
        self.port = config['port']
        if 'alert_channel' in config:
            app.config.update(alert_channel='#' + config['alert_channel'])
        threading.Thread.__init__(self, daemon=True)

    @staticmethod
    def set_connection(connection):
        app.config.update(irc_connection=connection)

    def run(self):
        if 'irc_connection' not in app.config:
            raise Exception('set_connection() must be called')
        logger.info(
            f"starting internal http server on {self.host}:{self.port}"
        )
        app.run(host=self.host, port=self.port, debug=False,
                use_reloader=False)


if __name__ == '__main__':
    class DummyConnection:
        @staticmethod
        def privmsg(target, msg):
            logger.info(f"sending PRIVMSG to '{target}': '{msg}'")

    t = HttpThread({'host': '127.0.0.1', 'port': 9999, 'alert_channel': 'alerts'})
    t.set_connection(DummyConnection)
    t.start()
    t.join()
