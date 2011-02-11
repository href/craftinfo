#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Test of the craftinfo module

"""

from __future__ import with_statement

import os
import sys
import imp
import unittest
import pdb

sys.path.append("./../")

from craftinfo.log import LogEvents, LogParser

LOGLINES = (
    "2010-11-30 19:55:15 [INFO] Starting craftinfo server version 0.2.6_02\n",
    "2010-11-30 20:18:30 [INFO] <user> chit chat\n",
    "2010-11-30 19:56:42 [INFO] user_test [/188.60.36.18:61540] logged in with entity id 24\n",
    "2010-11-30 19:56:42 [INFO] user_test [/188.60.36.18:61540] logged in with entity id 24\n",
    "2010-11-30 20:22:07 [INFO] anotheruser lost connection: Quitting\n",
    "\n",
    "\n"
)

MORELINES = (
    "\n",
    "\n",
    "2010-11-30 20:00:37 [WARNING] Can't keep up! Did the system time change, or is the server overloaded?\n",
    "2010-11-30 20:22:07 [INFO] user_test lost connection: Quitting\n"  
)

LOGFILE = "generated.log"


def generatelog():
    with open(LOGFILE, "w") as f:
        f.writelines(LOGLINES)


def appendlog():
    with open(LOGFILE, "a+") as f:
        f.writelines(MORELINES)


def removelog():
    os.remove(LOGFILE)


class TestLogParser(unittest.TestCase):
    def onlogin(self, player, time):
        self.logins += 1
    
    def test_generatedlog(self):
        #create log with testdata
        generatelog()

        events = LogEvents()

        self.logins = 0
        events.on_playerlogin = self.onlogin
        log = LogParser(LOGFILE, events)
        self.assertEqual(self.logins, 2)
        self.assertEqual(log.version, '0.2.6_02')

        players = log.get_playerlist()

        #test if the expected test-user is found
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0], "user_test")

        #add to the log
        appendlog()

        #get the new values of the log
        log.update()

        #check if the user was removed from the list
        players = log.get_playerlist()
        self.assertEqual(len(players), 0)

        #removing the logfile has to fail as info still has the handle
        self.assertRaises(OSError, removelog)

        del log

        #shouldn't throw an exception anymore
        removelog()

if __name__=="__main__":
    unittest.main()