#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Returns information about the Minecraft-Server (on href.ch)

The server needs to be run on the same computer. Currently, only Unix
is fully supported.

"""

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

def is_running():
    """Returns True if the Server is running.

    The used jar file for the server must contain 'minecraft_server'
    for the code to work.

    Windows is currently not supported as it doesn't yield enough
    information about running processes to use the same concept as
    used on Unix.
    
    """
    if os.name == "nt":
        return False

    for proc in get_proclist():
        if proc.find("minecraft_server") != -1:
            return True
        elif proc.find("bukkit") != -1:
            return True

    return False