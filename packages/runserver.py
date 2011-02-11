#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Runs a socket server that provides Minecraft-server info.

To start the server, the script has to be executed directly.
The server can then be controlled by commandline.

Entering 'help' after starting the server reveils these commands.

"""

import os
import time
import threading
from datetime import datetime

import gevent
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from craftinfoserver import generate_xml, EchoServer
from craftinfo.log import LogParser
from craftinfo.db.tables import Message, create_tables
from craftinfo.server import is_running

class CommandError(Exception):
    pass

class StopServer(CommandError):
    pass

def wait_for_input(result):
    """Waits for raw_input to return and sends the result to the
    eventlet.event given by parameter.

    """
    line = raw_input()
    result.set(line)

def run_server(logfile, database, port):
    """Runs the server and listenes to commands."""

    engine = create_engine(database)
    create_tables(engine)

    session = sessionmaker(bind=engine)()

    log = LogParser(logfile)

    # definition of callback function
    def get_value():
        msgs = session.query(Message).order_by(desc(Message.date))
        return generate_xml(is_running, log, session, msgs) 

    srv = EchoServer(port, get_value)
    srv.start()

    cmds = Commands(srv, session)

    print 'started'

    # run raw_input in a different thread and handle incoming inputs
    while True:    
        result = gevent.event.AsyncResult()
        t = threading.Thread(target=wait_for_input, args=(result,))
        
        t.start()
        
        while t.isAlive():
            gevent.sleep(1)

        try:
            handle_command(cmds, result.get())
        except StopServer:
            break

def handle_command(cmds, commandline):
    """Handles the input of the server-commandline, executing commands."""
    cmd = commandline.split(" ")[0].strip()
    args = commandline.replace(cmd, "").strip()

    if cmd != "":
        cmds[cmd](args)

class Commands(object):
    """Every public member-period is available as server command.

    To add a new server-command, just add a method not beginning with an
    underscore that takes self and arg as an argument.

    Added methods can be called like this:
    c = Commands()
    c["help"](args)

    Args being the string of arguments for the given functions.

    Thusly, the command-string directly translates to the name of the
    function.

    """
    def __init__(self, srv, session):
        """ Initialize the instance with the needed context. """
        self.srv = srv
        self.session = session

        is_method = lambda attr: callable(getattr(self, attr))
        is_public = lambda attr: not attr.startswith('_')

        fn = [m for m in dir(self) if is_method(m) and is_public(m)]
        fn.sort()
        
        self._cmds = dict([(fn, getattr(self, fn)) for fn in fn])
            
    def __getitem__(self, key):
        """ Return the command if found or a function that prints 
        'unknown command'. """
        try:
            return self._cmds[key]
        except KeyError:
            return self._unknown

    def __contains__(self, item):
        return item in self._cmds

    def _unknown(self, item):
        print "unknown command"

    def help(self, args):
        """ Displays available commands. """
        functions = self._cmds.keys()
        functions.sort()
        for fn in functions:
            print "%s\t%s" % (fn, self._cmds[fn].__doc__)

    def stop(self, args):
        """ Stops the server gracefully. """
        self.srv.stop()
        raise StopServer

    def show(self, args):
        """ Shows log-messages in the console. """
        self.srv.show_output = True

    def hide(self, args):
        """ Hides log-messages in the console. """
        self.srv.show_output = False

    def add(self, args):
        """ Addes a message with the current time. """
        if args != "":
            self.session.add(Message(datetime.now(), args))
            self.session.commit()

    def list(self, args):
        """ Lists current messages. """
        for m in self.session.query(Message).all():
            print m

    def delete(self, args):
        """ Removes a message by id. """
        if args != "":
            msg = self.session.query(Message).filter(Message.uid==args)
            msg.delete()
            self.session.commit()

    def value(self, args):
        """ Shows the current xml value of the server. """
        print self.srv.value

if __name__=='__main__':
    #Port to listen to
    port = 5001

    # Database to write updates in
    database = 'sqlite:///db.sqlite'

    # Location of minecraft server logfile
    if os.name == 'nt':
        logfile = './server.log'
    else:    
        logfile = '/home/denis/minecraft/server.log'

    run_server(logfile, database, port)
    
