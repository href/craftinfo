#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys
import gevent

sys.path.append("./../")

from craftinfoserver import EchoServer, get_servervalue

class TestServer(unittest.TestCase):

    def test_server(self):
        get_result = lambda: "deadbeef"
        srv = EchoServer(1234, get_result)
        srv.start()

        direct_result = get_result()

        request = gevent.spawn(get_servervalue, "localhost", 1234)
        while not request.ready():
            gevent.sleep(0)
        
        request_result = request.value

        self.assertEqual(direct_result, request_result)

if __name__=="__main__":
    unittest.main()