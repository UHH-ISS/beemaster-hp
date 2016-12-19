# -*- coding: utf-8 -*-
"""tests.py

Provides various tests for the connector.
"""
from __future__ import with_statement

from mapper import Mapper

import unittest
import pybroker as pb
from datetime import datetime
import yaml


class TestMapper(unittest.TestCase):
    """TestCases for mapper.Mapper."""

    VALID_INPUT_1 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                     {"connection": {"remote_ip": "127.0.0.1",
                                     "remote_hostname": "", "id": 3019197952,
                                     "protocol": "pcap", "local_port": 4101,
                                     "local_ip": "127.0.0.1", "remote_port":
                                     35324, "transport": "tcp"}}, "name":
                     "dionaea", "origin": "dionaea.connection.free"}
    VALID_INPUT_2 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                     {"connection": {"remote_ip": "2001:0:509c:564e:34ae:3a9a:3f57:fd91",
                                     "remote_hostname": "", "id": 3019197952,
                                     "protocol": "pcap", "local_port": 4101,
                                     "local_ip": "127.0.0.1", "remote_port":
                                     35324, "transport": "tcp"}}, "name":
                     "dionaea", "origin": "dionaea.connection.free"}
    INVALID_INPUT_1 = {"origin": "dionaea.connection.link", "timestamp":
                       "2016-12-09T21:11:09.315143",
                       "data": {"parent": {"protocol": "httpd", "local_port":
                                           80, "local_ip": "127.0.0.1",
                                           "remote_hostname": "",
                                           "remote_port": 0, "id":
                                           140386985909024, "transport": "tcp",
                                           "remote_ip": ""},
                                "child": {"protocol": "httpd", "local_port":
                                          80, "local_ip": "127.0.0.1",
                                          "remote_hostname": "", "remote_port":
                                          59268, "id": 140386985908744,
                                          "transport": "tcp", "remote_ip":
                                          "127.0.0.1"}},
                       "name": "dionaea"}
    INVALID_INPUT_2 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "12.12.12.12.12.12",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}
    INVALID_INPUT_3 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "127.0.0.1",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port": "4101",
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}
    INVALID_INPUT_4 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "12...12",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}

    VALID_MAPPING = 'mappings/dionaea/connection.yaml'

    def setUp(self):
        """Set up the default mapper."""
        with open(self.VALID_MAPPING, 'r') as f:
            mapping = yaml.load(f)
        self.mapper = Mapper([mapping])     # [..] necessary as of format

    def testDefaultSuccess(self):
        """Test the default successful scenario."""
        def _map_time(inp):
            date = datetime.strptime(inp, '%Y-%m-%dT%H:%M:%S.%f')
            return pb.time_point((date - datetime.utcfromtimestamp(0))
                                 .total_seconds())

        def _map_addr(inp):
            return pb.address_from_string(inp)

        expect = map(pb.data, (_map_time("2016-11-26T22:18:56.281464"),
                               3019197952, _map_addr("127.0.0.1"), 4101,
                               _map_addr("127.0.0.1"), 35324, "tcp"))

        message = pb.message()
        for i in expect:
            message.append(i)

        result = self.mapper.transform(self.VALID_INPUT_1)
        #while not message.empty():
        #    print(message.pop())
        #    print(result.pop())
        while not message.empty():
            self.assertEqual(str(message.pop()), str(result.pop()))

    def testDefaultSuccess2(self):
        """Test the default successful scenario."""
        def _map_time(inp):
            date = datetime.strptime(inp, '%Y-%m-%dT%H:%M:%S.%f')
            return pb.time_point((date - datetime.utcfromtimestamp(0))
                                 .total_seconds())

        def _map_addr(inp):
            return pb.address_from_string(inp)

        expect = map(pb.data, (_map_time("2016-11-26T22:18:56.281464"),
                               3019197952, _map_addr("127.0.0.1"), 4101,
                               _map_addr("2001:0:509c:564e:34ae:3a9a:3f57:fd91"), 35324, "tcp"))

        message = pb.message()
        for i in expect:
            message.append(i)

        result = self.mapper.transform(self.VALID_INPUT_2)
        #while not message.empty():
        #    print(message.pop())
        #    print(result.pop())
        while not message.empty():
            self.assertEqual(str(message.pop()), str(result.pop()))

    def testFailureUnexpectedContent(self):
        """Test empty output on an non-matching message."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_1))

    def testFailureIPTooLong(self):
        """Test empty output on an non-matching message."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_2))

    def testFailureCountIsString(self):
        """Test empty output on an non-matching message."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_3))

    def testFailureIPMissingBytes(self):
        """Test empty output on an non-matching message."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_4))

    def testMissingField(self):
        """Test empty output on message, missing a field."""
        del self.VALID_INPUT_1['timestamp']

        self.assertIsNone(self.mapper.transform(self.VALID_INPUT_1))

    # TODO require tests for:
    #       - multiple mappings
    #       - different inputs
    #       - invalid mappings


if __name__ == '__main__':
    unittest.main()
