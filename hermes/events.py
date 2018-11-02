"""
Module that contains all of the different types of events that hermes can act upon. Useful just
for ensuring consistency in reference to the events across the hermes codebase. The events should
always be lowercased with an uppercase const reference.
"""


class Events(object):
    PRIVMSG = "privmsg"
    PUBMSG = "pubmsg"
