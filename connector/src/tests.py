# -*- coding: utf-8 -*-
"""tests.py

Provides various tests for the connector.
"""
from __future__ import with_statement

from mapper import Mapper
from connector import ConnConfig

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
                     {"connection": {"remote_ip":
                                     "2001:0:509c:564e:34ae:3a9a:3f57:fd91",
                                     "remote_hostname": "", "id": 3019197952,
                                     "protocol": "ftp", "local_port": 0,
                                     "local_ip": "127.0.0.1", "remote_port":
                                     65535, "transport": "tcp"}}, "name":
                     "dionaea", "origin": "dionaea.connection.free"}
    VALID_INPUT_3 = {"timestamp": "2016-11-26T22:18:56.281464", "origin":
                     "dionaea.connection.free"}
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
                       {"connection": {"remote_ip": "12.12.12.12.12",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}
    INVALID_INPUT_3 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "127.0.0.1",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port":
                                       "4101",
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
    INVALID_INPUT_5 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "127.0.0.1",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       353242, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}
    INVALID_INPUT_6 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "127.0.0.1",
                                       "remote_hostname": "", "id": 300.212354,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}

    VALID_MAPPING = 'mappings/dionaea/connection.yaml'
    VALID_MAPPING2 = 'mappings/dionaea/connectionTest.yaml'

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

        expect = map(pb.data, ("dionaea_connection",
                               _map_time("2016-11-26T22:18:56.281464"),
                               3019197952, _map_addr("127.0.0.1"), 4101,
                               _map_addr("127.0.0.1"), 35324, "tcp"))

        message = pb.message()
        for i in expect:
            message.append(i)

        result = self.mapper.transform(self.VALID_INPUT_1)

        while not message.empty() or not result.empty():
            self.assertEqual(str(message.pop()), str(result.pop()))

    def testDefaultSuccess2(self):
        """Test another default successful scenario."""
        def _map_time(inp):
            date = datetime.strptime(inp, '%Y-%m-%dT%H:%M:%S.%f')
            return pb.time_point((date - datetime.utcfromtimestamp(0))
                                 .total_seconds())

        def _map_addr(inp):
            return pb.address_from_string(inp)

        expect = map(pb.data, ("dionaea_connection",
                               _map_time("2016-11-26T22:18:56.281464"),
                               3019197952, _map_addr("127.0.0.1"), 0,
                               _map_addr("2001:0:509c:564e:34ae:3a9a:3f57:"
                                         "fd91"), 65535, "tcp"))

        message = pb.message()
        for i in expect:
            message.append(i)

        result = self.mapper.transform(self.VALID_INPUT_2)

        while not message.empty() or not result.empty():
            self.assertEqual(str(message.pop()), str(result.pop()))

    def testSuccessMultipleMappings(self):
        """Test a scenario with more than one mapping."""
        def _map_time(inp):
            date = datetime.strptime(inp, '%Y-%m-%dT%H:%M:%S.%f')
            return pb.time_point((date - datetime.utcfromtimestamp(0))
                                 .total_seconds())

        with open(self.VALID_MAPPING, 'r') as f:
            mapping = yaml.load(f)
        with open(self.VALID_MAPPING2, 'r') as f:
            mapping2 = yaml.load(f)
        mapper = Mapper([mapping, mapping2])     # [..] necessary as of format

        expect = map(pb.data, ("dionaea_connection2",
                               _map_time("2016-11-26T22:18:56.281464")))

        message = pb.message()
        for i in expect:
            message.append(i)

        result = mapper.transform(self.VALID_INPUT_3)

        while not message.empty() or not result.empty():
            self.assertEqual(str(message.pop()), str(result.pop()))

    def testSuccessMultipleMappingsInverseOrder(self):
        """Test a scenario with more than one mapping in a different order."""
        def _map_time(inp):
            date = datetime.strptime(inp, '%Y-%m-%dT%H:%M:%S.%f')
            return pb.time_point((date - datetime.utcfromtimestamp(0))
                                 .total_seconds())

        with open(self.VALID_MAPPING, 'r') as f:
            mapping = yaml.load(f)
        with open(self.VALID_MAPPING2, 'r') as f:
            mapping2 = yaml.load(f)
        mapper = Mapper([mapping2, mapping])     # [..] necessary as of format

        expect = map(pb.data, ("dionaea_connection2",
                               _map_time("2016-11-26T22:18:56.281464")))

        message = pb.message()
        for i in expect:
            message.append(i)

        result = mapper.transform(self.VALID_INPUT_3)

        while not message.empty() or not result.empty():
            self.assertEqual(str(message.pop()), str(result.pop()))

    def testFailureUnexpectedContent(self):
        """Test empty output on an non-matching message."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_1))

    def testFailureIPTooLong(self):
        """Test empty output when the IP is too long."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_2))

    def testFailureCountIsString(self):
        """Test empty output when an expected count is a string."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_3))

    def testFailureIPMissingBytes(self):
        """Test empty output when the IP is missing bytes."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_4))

    def testFailureInvalidPort(self):
        """Test empty output when the port is out of bounds."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_5))

    def testFailureCountIsFloat(self):
        """Test empty output when an expected count is a float."""
        self.assertIsNone(self.mapper.transform(self.INVALID_INPUT_6))

    def testFailureWrongFieldType(self):
        """Wrong Field type

        Test empty output when a field in the mapping is wrong
        and the message therefore unexpected.
        """
        with open(self.VALID_MAPPING, 'r') as f:
            mapping = yaml.load(f)
        mapping['mapping']['data'] = 'count'
        mapper = Mapper([mapping])     # [..] necessary as of format

        self.assertIsNone(mapper.transform(self.VALID_INPUT_1))

    def testFailureInvalidConversionFunc(self):
        """Test empty output when a conversion function is invalid."""
        with open(self.VALID_MAPPING, 'r') as f:
            mapping = yaml.load(f)
        mapping['mapping']['data']['connection']['id'] = 'list'
        mapper = Mapper([mapping])     # [..] necessary as of format

        self.assertIsNone(mapper.transform(self.VALID_INPUT_1))

    def testMissingField(self):
        """Test empty output on message, missing a field."""
        del self.VALID_INPUT_1['timestamp']

        self.assertIsNone(self.mapper.transform(self.VALID_INPUT_1))

    # TODO require tests for:
    #       - multiple mappings
    #       - different inputs
    #       - invalid mappings


class TestConnConfig(unittest.TestCase):
    """TestCases for connector.ConnConfig"""

    def testDefaultSuccess(self):
        """Test if default values are properly returned"""
        cc = ConnConfig()

        self.assertEqual('mappings', cc.mappings)
        self.assertEqual('0.0.0.0', cc.listen['address'])
        self.assertEqual(8080, cc.listen['port'])
        self.assertEqual('127.0.0.1', cc.send['address'])
        self.assertEqual(5000, cc.send['port'])
        self.assertEqual('honeypot/dionaea/', cc.broker['topic'])
        self.assertEqual('dioEp', cc.broker['endpoint'])

    def testSuccessUpdate(self):
        """Update Success

        Test if default values still work if some are replaced.
        Also if replacing values works
        """
        cc = ConnConfig()

        cc.update({'mappings': 'dionaea', 'listen': {'port': 0,
                                                     'address': 'test'}})

        self.assertEqual('dionaea', cc.mappings)
        self.assertEqual('test', cc.listen['address'])
        self.assertEqual(0, cc.listen['port'])
        self.assertEqual('127.0.0.1', cc.send['address'])
        self.assertEqual(5000, cc.send['port'])
        self.assertEqual('honeypot/dionaea/', cc.broker['topic'])
        self.assertEqual('dioEp', cc.broker['endpoint'])

    def testSuccessInitUpdate(self):
        """Initialization Update Success

        Test if default values still work if some are
        replaced at the initialization
        """
        cc = ConnConfig({'mappings': 'dionaea', 'listen': {'port': 7080,
                                                           'address': 'test'}})

        self.assertEqual('dionaea', cc.mappings)
        self.assertEqual('test', cc.listen['address'])
        self.assertEqual(7080, cc.listen['port'])
        self.assertEqual('127.0.0.1', cc.send['address'])
        self.assertEqual(5000, cc.send['port'])
        self.assertEqual('honeypot/dionaea/', cc.broker['topic'])
        self.assertEqual('dioEp', cc.broker['endpoint'])

    def testSuccessMissingValue(self):
        """Missing Value Success

        Test value must not be missing after a nested key
        is only partially replaced
        """
        cc = ConnConfig()

        cc.update({'listen': {'port': 7080}})

        self.assertEqual('mappings', cc.mappings)
        self.assertTrue('address' in cc.listen)
        self.assertEqual('0.0.0.0', cc.listen['address'])
        self.assertEqual(7080, cc.listen['port'])
        self.assertEqual('127.0.0.1', cc.send['address'])
        self.assertEqual(5000, cc.send['port'])
        self.assertEqual('honeypot/dionaea/', cc.broker['topic'])
        self.assertEqual('dioEp', cc.broker['endpoint'])

    def testFailureInvalidKey(self):
        """Invalid Key Failure

        Test exception being thrown when a key for
        updating the config is invalid (should not exist)
        """
        cc = ConnConfig()

        self.assertRaises(Exception, cc.update, {'mappings': 'dionaea',
                                                 'address': 5000,
                                                 'listennnnn': {'port': 8080}})


if __name__ == '__main__':
    unittest.main()
