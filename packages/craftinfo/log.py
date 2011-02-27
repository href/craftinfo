from __future__ import with_statement

import os
import re
from datetime import datetime
from time import strptime
from itertools import imap

from gevent import socket
import xml.etree.ElementTree as ET

from craftinfo.proc import get_proclist
import craftinfo.db.tables as tables

class LogEvents(object):
    """Provides a list with events triggered by the LogParser.

    Each class-member can be set to a certain function, which will be
    called if an instance of LogEvents is passed to the LogParser.

    """
    __slots__ = (
        'on_playerlogin',
        'on_playerlogout',
        'on_serverstart',
        )

    # TODO get rid of duplicated code by changing the __init__ function 
    # to automatically check and set the arguments from **kargs

    def __init__(self):
        self.on_playerlogin = lambda player, date: None
        self.on_playerlogout = lambda player, date: None
        self.on_serverstart = lambda version, date: None

class LogParser(object):
    """Reads the Minecraft server log incrementally, keeping a playerlist
    and the last start time of the server.

    """
    def __init__(self, path, logevents=LogEvents()):
        """Reads the logfile given by argument."""
        self.path = path
        self.follow = None
        self.events = logevents
        self.reset()
        self.update()
        
    def __del__(self):
        """Ensures that the file-handle is released upon deletion."""
        self._stopfollowing()

    def _stopfollowing(self):
        """Signals the follower generator to stop and close the file."""
        if self.follow:
            self.follow.close()

    def reset(self):
        """Resets the class. Lines are deleted and reading starts from
        the beginning of the file again.

        """
        self._players = dict()
        self._startime = datetime
        self._version = None
        
        self._stopfollowing()

        self.follower = _follow(self.path)

    def update(self):
        """Reads through the logfile in increments and stores 
       the results.

        Will remember the position of the last read and resume if called
        again, adding to the list of filtered lines. If reset is called
        before the lines are reloaded.

        """
        if not os.path.exists(self.path):
            return

        for line in self.follower:
            # If the line is None the follower is done, for now.
            # So don't be clever and change this into a list comprehension
            # as it will result in an endless loop
            if not line:
                break

            # Chatlines might contain stuff that triggers commands later
            if self._is_chatline(line):
                continue
            
            # If a player joins, add him to the list.
            player = self._get_playerlogin(line)
            if player:
                login = self._get_date(line)
                self._players[player] = login

                self.events.on_playerlogin(player, login)
                continue

            # If a player leaves, remove him from the list.
            player = self._get_playerlogout(line)
            if player and player in self._players:    
                logout = self._get_date(line)
                del self._players[player]

                self.events.on_playerlogout(player, logout)
                continue

            # Update the starttime (the last is always the latests).
            if 'Starting' in line:
                self._starttime = self._get_date(line)
                self.version = self._get_serverversion(line)

                # clear the playerlist as there cannot be any connected
                # player on startup
                self._players.clear()
                self.events.on_serverstart(self.version, self._starttime)
                continue

    def get_playerlist(self):
        return self._players.keys()

    def get_players(self):
        return self._players

    def _get_date(self, line):
        """Returns the date from a given log-line"""
        return strptime(line[:19], "%Y-%m-%d %H:%M:%S")

    def _get_playerlogin(self, line):
        """Returns the playername if the player joined on the given line.

        Otherwise None is returned

        """
        m = re.search("\[INFO\]\s([a-zA-Z0-9_]*)\s.*logged in", line)
        if m == None:
            return None
        else:
            return m.groups(0)[0]
    
    def _get_playerlogout(self, line):
        """Returns the playername if the player left on the given line.

        Otherwise None is returned

        """
        m = re.search("\[INFO\]\s([a-zA-Z0-9_]*)\s.*lost connection", line)

        if m == None:
            return None
        else:
            return m.groups(0)[0]   

    def _get_serverversion(self, line):
        """ Returns the serverversion or None. """
        m = re.search("server version (\S*)", line)
        if m == None:
            return None
        else:
            return m.groups(0)[0]

    def _is_chatline(self, line):
        return '<' in line


def _follow(logfile):
    """ Yields the lines of the givenfile indefinitely.

    If the yield is None the function read until the end. However,
    if new lines are appended, those will again be yielded. Being a
    generator this function keeps the file open until the close method
    is called on the generator.

    """
    try:
        with open(logfile, "rb") as f:
            while True:
                yield f.readline()
    except GeneratorExit:
        pass