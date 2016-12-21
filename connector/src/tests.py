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

    # TODO We should find an easier way to have all those inputs.
    #      One possibility: Only have one valid input and modify
    #      it in each test function to the relevant version.
    VALID_INPUT_1 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                     {"connection": {"remote_ip": "127.0.0.1",
                                     "remote_hostname": "", "id": 3019197952,
                                     "protocol": "pcap", "local_port": 4101,
                                     "local_ip": "127.0.0.1", "remote_port":
                                     35324, "transport": "tcp"}}, "name":
                     "dionaea", "origin": "dionaea.connection.free"}
    # remote as IPv6
    VALID_INPUT_2 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                     {"connection": {"remote_ip":
                                     "2001:0:509c:564e:34ae:3a9a:3f57:fd91",
                                     "remote_hostname": "", "id": 3019197952,
                                     "protocol": "ftp", "local_port": 0,
                                     "local_ip": "127.0.0.1", "remote_port":
                                     65535, "transport": "tcp"}}, "name":
                     "dionaea", "origin": "dionaea.connection.free"}
    # minimal
    VALID_INPUT_3 = {"timestamp": "2016-11-26T22:18:56.281464", "origin":
                     "dionaea.connection.free"}
    # missing keys (wrong layer)
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
    # invalid IPv4 address
    INVALID_INPUT_2 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "12.12.12.12.12",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}
    # port is a string
    INVALID_INPUT_3 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "127.0.0.1",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port":
                                       "4101",
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}
    # invalid remote IP
    INVALID_INPUT_4 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "12...12",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}
    # port is out of bounds
    INVALID_INPUT_5 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "127.0.0.1",
                                       "remote_hostname": "", "id": 3019197952,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       353242, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}
    # id is a float
    INVALID_INPUT_6 = {"timestamp": "2016-11-26T22:18:56.281464", "data":
                       {"connection": {"remote_ip": "127.0.0.1",
                                       "remote_hostname": "", "id": 300.212354,
                                       "protocol": "pcap", "local_port": 4101,
                                       "local_ip": "127.0.0.1", "remote_port":
                                       35324, "transport": "tcp"}}, "name":
                       "dionaea", "origin": "dionaea.connection.free"}

    VALID_MAPPING = 'mappings/dionaea/connection.yaml'
    VALID_MAPPING2_DICT = {"name": "dionaea_connection2", "mapping":
                           {"timestamp": "time_point", "origin": "string"},
                           "message": ["timestamp"]}

    @staticmethod
    def _map_time(inp):
        date = datetime.strptime(inp, '%Y-%m-%dT%H:%M:%S.%f')
        return pb.time_point((date - datetime.utcfromtimestamp(0))
                             .total_seconds())

    @staticmethod
    def _map_addr(inp):
        return pb.address_from_string(inp)

    def _compare_messages(self, mapper, expect, inp):
        """Compare messages

        :param mapper:  The mapper to use (mapper.Mapper)
        :param expect:  The values to expect (Iter[pd.data])
        :param inp:     The input to map to (Dict)
        """
        message = pb.message()
        for i in expect:
            message.append(i)

        result = mapper.transform(inp)

        while not message.empty() and not result.empty():
            self.assertEqual(str(message.pop()), str(result.pop()))

    def setUp(self):
        """Set up the default mapper."""
        with open(self.VALID_MAPPING, 'r') as f:
            mapping = yaml.load(f)
        self.mapper = Mapper([mapping])     # [..] necessary as of format

    def testDefaultSuccess(self):
        """Test the default successful scenario."""
        # TODO we should pull those values from the input, we are going to
        # read... as it is, it is destined to fail on any small change...
        expect = map(pb.data,
                     ("dionaea_connection",
                      TestMapper._map_time("2016-11-26T22:18:56.281464"),
                      3019197952, TestMapper._map_addr("127.0.0.1"), 4101,
                      TestMapper._map_addr("127.0.0.1"), 35324, "tcp"))

        self._compare_messages(self.mapper, expect, self.VALID_INPUT_1)

    def testDefaultSuccessIPv6(self):
        """Test default scenario with IPv6 address."""
        expect = map(pb.data,
                     ("dionaea_connection",
                      TestMapper._map_time("2016-11-26T22:18:56.281464"),
                      3019197952, TestMapper._map_addr("127.0.0.1"), 0,
                      TestMapper._map_addr("2001:0:509c:564e:34ae:3a9a:3f57:"
                                           "fd91"), 65535, "tcp"))

        self._compare_messages(self.mapper, expect, self.VALID_INPUT_2)

    def testSuccessMultipleMappings(self):
        """Test a scenario with more than one mapping."""
        with open(self.VALID_MAPPING, 'r') as f:
            mapping = yaml.load(f)
        mapping2 = self.VALID_MAPPING2_DICT
        mapper = Mapper([mapping, mapping2])

        # works, as mapping2 is way more relaxed than the default mapping
        expect = map(pb.data,
                     ("dionaea_connection2",
                      TestMapper._map_time("2016-11-26T22:18:56.281464")))

        self._compare_messages(mapper, expect, self.VALID_INPUT_3)

    def testSuccessMultipleMappingsInverseOrder(self):
        """Test a scenario with more than one mapping in a different order."""
        with open(self.VALID_MAPPING, 'r') as f:
            mapping = yaml.load(f)
        mapping2 = self.VALID_MAPPING2_DICT
        mapper = Mapper([mapping2, mapping])

        expect = map(pb.data,
                     ("dionaea_connection2",
                      TestMapper._map_time("2016-11-26T22:18:56.281464")))

        self._compare_messages(mapper, expect, self.VALID_INPUT_3)

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
        # also test with negative number
        self.INVALID_INPUT_5['data']['connection']['remote_port'] = -1
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


class TestConnConfig(unittest.TestCase):
    """TestCases for connector.ConnConfig"""

    def setUp(self):
        """Set up the default setup"""
        self.default = ConnConfig.DEFAULT_CONFIG
        # TODO Should perform deep copy of dict, in case ConnConfig would
        #      change it during __init__.
        self.config = ConnConfig()

    def testDefaultSuccess(self):
        """Test if default values are properly returned"""
        dc = self.default
        cc = self.config

        self.assertEqual(dc['mappings'], cc.mappings)
        self.assertEqual(dc['listen']['address'], cc.listen.address)
        self.assertEqual(dc['listen']['port'], cc.listen.port)
        self.assertEqual(dc['send']['address'], cc.send.address)
        self.assertEqual(dc['send']['port'], cc.send.port)
        self.assertEqual(dc['broker']['topic'], cc.broker.topic)
        self.assertEqual(dc['broker']['endpoint'], cc.broker.endpoint)
        self.assertEqual(dc['connectorId'], cc.connectorId)

    def testSuccessUpdate(self):
        """Update Success

        Test if default values still work if some are replaced.
        Also if replacing values works.
        """
        dc = self.default
        cc = self.config
        cc.update({'mappings': 'dionaea',
                   'listen': {'port': 0, 'address': 'test'}})

        self.assertEqual('dionaea', cc.mappings)
        self.assertEqual('test', cc.listen.address)
        self.assertEqual(0, cc.listen.port)
        self.assertEqual(dc['send']['address'], cc.send.address)
        self.assertEqual(dc['send']['port'], cc.send.port)
        self.assertEqual(dc['broker']['topic'], cc.broker.topic)
        self.assertEqual(dc['broker']['endpoint'], cc.broker.endpoint)
        self.assertEqual(dc['connectorId'], cc.connectorId)

    def testSuccessInitUpdate(self):
        """Initialization Update Success

        Test if default values still work if some are
        replaced at the initialization
        """
        dc = self.default
        cc = ConnConfig({'mappings': 'dionaea', 'listen': {'port': 7080,
                                                           'address': 'test'}})

        self.assertEqual('dionaea', cc.mappings)
        self.assertEqual('test', cc.listen.address)
        self.assertEqual(7080, cc.listen.port)
        self.assertEqual(dc['send']['address'], cc.send.address)
        self.assertEqual(dc['send']['port'], cc.send.port)
        self.assertEqual(dc['broker']['topic'], cc.broker.topic)
        self.assertEqual(dc['broker']['endpoint'], cc.broker.endpoint)
        self.assertEqual(dc['connectorId'], cc.connectorId)

    def testSuccessMissingValue(self):
        """Missing Value Success

        Test value must not be missing after a nested key
        is only partially replaced
        """
        dc = self.default
        cc = ConnConfig({'listen': {'port': 7080}})

        # the essential check:
        self.assertTrue('address' in cc.listen)
        self.assertEqual(dc['listen']['address'], cc.listen.address)
        self.assertEqual(7080, cc.listen.port)

        # testing unrelated defaults:
        self.assertEqual(dc['send']['address'], cc.send.address)
        self.assertEqual(dc['mappings'], cc.mappings)
        # We already have tests for the general behaviour of ConnConfig. We do
        # not need to test everything everytime.

    def testFailureInvalidKey(self):
        """Invalid Key Failure

        Test exception being thrown when a key for
        updating the config is invalid (should not exist)
        """
        # TODO maybe specify to something like ArgumentException or
        #      KeyLookupError or something similar...
        self.assertRaises(Exception, self.config.update,
                          {'mappings': 'dionaea', 'address': 5000,
                           'listennnnn': {'port': 8080}})


if __name__ == '__main__':
    unittest.main()
