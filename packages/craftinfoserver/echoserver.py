#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Socket-server that echoes any string.

Listens on a configured port and returns the value from a 
callback function.

The requested information is preemptively cached each 30 seconds.

"""

import os
import time
from datetime import datetime

import gevent
import gevent.event
from gevent import socket

class EchoServer():
    """Socketserver echoing any string value on any specified port.

    The string to be echoed is the result of the callback function
    object passed on construction. This callback function will be called
    each 30 seconds per default. This interval can be changed anytime.

    """

    def __init__(self, port, callback, interval=30):
        """Takes the logfile to read and the port to listen to.

        arguments:
        port -- port to listen on
        callback -- function to call for the echo-value (no parameters)
        interval -- interval in seconds with which callback will be polled
        
        """
        self.port = port
        self.show_output = True
        self.interval = 30
        self._stop = False        
        self._callback = callback
    
    def stop(self):
        """Causes the server to stop."""
        self._stop = True
        print "stopping"
        self._cacheloop.kill()
        self._mainloop.join()
        self.socket.close()
    
    def start(self):
        """Start the server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # For some reason the sockets are closed by the system gc on unix
        # instead of the python gc, resulting in sockets that are kept open
        # after shutting down the server. Until this is solved, reuse
        # addresses to enable fast restarting.
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.socket.bind(('', self.port))
        self.socket.listen(5)
        self.socket.settimeout(1)

        self._cacheloop = gevent.spawn(self._cache_forever)
        self._mainloop = gevent.spawn(self._serve_forever)

    def _cache_forever(self):
        """ Gets the value of the callback in the given interval until
        the server is stopped. """
        while not self._stop:
            get = gevent.spawn(self._callback)
            while not get.ready():
                gevent.sleep(0)

            self.value = get.value
            gevent.sleep(self.interval)
            
    def _handle_connection(self, new_socket):
        """ Writes the value to the client-socket, making sure it is
        closed afterwards. """
        try:
            new_socket.send(self.value)
        finally:
            new_socket.close()
    
    def _print_connection(self, address, starttime):
        """ Prints a connection log. """
        if self.show_output:
            endtime = (self._get_tick() - starttime) * 1000
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            print u"%s\t%s\t%.3fms" % (timestamp, address[0], endtime)
    
    def _get_tick(self):
        """ Returns a timetick for performance tests depending on the os.

        time.clock on windows behaves like time.time on unix. To measure
        time in a high resolution without timeit, this little indirection
        is needed.

        """
        if os.name == 'nt':
            return time.clock()
        else:
            return time.time()

    def _serve_forever(self):
        """Main-loop handling incoming connections."""
        while not self._stop:
            try:
                new_socket, address = self.socket.accept()
                starttime = self._get_tick()
                gevent.spawn_raw(self._handle_connection, new_socket)
                gevent.spawn_raw(self._print_connection, address, starttime)
            except (socket.timeout, socket.error):
                pass
            finally:
                gevent.sleep(0)

        self.socket.close()
        print "goodbye, cruel world"