from mapper import Mapper

import unittest
import pybroker as pb

import logging
from datetime import datetime
import yaml
import re
from copy import deepcopy

class TestMapper(unittest.TestCase):
    """TestCases for mapper.Mapper."""

    TEST_DATE_STRING = "2017-01-01T00:00:00.000000"
    TEST_IPV4 = "127.0.0.1"
    TEST_IPV6 = "2001:0:509c:564e:34ae:3a9a:3f57:fd91"
    TEST_PORT = 1234
    TEST_STRING = "FOO"
    TEST_NUMBER = 123456789
    TEST_ARRAY = ["some hopefully escaped``` string;;--\"", "[]{}sth else;`~^"]

    # all default datatypes
    VALID_INPUT_PLAIN = {
        "timestamp":  TEST_DATE_STRING,
        "ipv4": TEST_IPV4,
        "ipv6": TEST_IPV6,
        "port": TEST_PORT,
        "string": TEST_STRING,
        "number": TEST_NUMBER,
        "array": TEST_ARRAY
    }

    VALID_MAPPING_PLAIN = yaml.load("""
        name: plain
        mapping:
            timestamp: time_point
            ipv4: address
            ipv6: address
            port: port_count
            string: string
            number: count
            array: array
        message:
            - timestamp
            - ipv4
            - ipv6
            - port
            - string
            - number
            - array
    """)

    VALID_INPUT_NESTED = {
        "nested": {
            "deeper": {
                "timestamp": TEST_DATE_STRING,
                "ipv4": TEST_IPV4,
                "ipv6": TEST_IPV6,
                "port": TEST_PORT,
                "string": TEST_STRING,
                "number": TEST_NUMBER,
                "array": TEST_ARRAY
            }
        }
    }

    VALID_MAPPING_NESTED = yaml.load("""
        name: nested
        mapping:
            nested:
                deeper:
                    timestamp: time_point
                    ipv4: address
                    ipv6: address
                    port: port_count
                    string: string
                    number: count
                    array: array
        message:
            - timestamp
            - ipv4
            - ipv6
            - port
            - string
            - number
            - array
    """)

    @staticmethod
    def _validate_map_time(inp):
        date = datetime.strptime(inp, '%Y-%m-%dT%H:%M:%S.%f')
        return pb.time_point((date - datetime.utcfromtimestamp(0))
                             .total_seconds())

    @staticmethod
    def _validate_map_addr(inp):
        return pb.address_from_string(inp)

    @staticmethod
    def _validate_map_array(inp):
        string = ";".join(inp)
        string = re.sub(r"\s+", ' ', string)
        return str(string)


    VALID_MAPPING_MYSQL = 'mappings/dionaea/mysql.yaml'

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

    def testPlainMapSuccess(self, mapper=Mapper([VALID_MAPPING_PLAIN])):
        """Test the default successful scenario."""
        expect = map(pb.data, (
                        self.VALID_MAPPING_PLAIN.get('name'),
                        TestMapper._validate_map_time(self.TEST_DATE_STRING),
                        TestMapper._validate_map_addr(self.TEST_IPV4),
                        TestMapper._validate_map_addr(self.TEST_IPV6),
                        self.TEST_PORT,
                        self.TEST_STRING,
                        self.TEST_NUMBER,
                        TestMapper._validate_map_array(self.TEST_ARRAY)
                    )
                )

        self._compare_messages(mapper, expect, self.VALID_INPUT_PLAIN)

    def testNestedMapSuccess(self, mapper=Mapper([VALID_MAPPING_NESTED])):
        """Test the default successful scenario."""
        expect = map(pb.data, (
                        self.VALID_MAPPING_NESTED.get('name'),
                        TestMapper._validate_map_time(self.TEST_DATE_STRING),
                        TestMapper._validate_map_addr(self.TEST_IPV4),
                        TestMapper._validate_map_addr(self.TEST_IPV6),
                        self.TEST_PORT,
                        self.TEST_STRING,
                        self.TEST_NUMBER,
                        TestMapper._validate_map_array(self.TEST_ARRAY)
                    )
                )

        self._compare_messages(mapper, expect, self.VALID_INPUT_NESTED)

    def testSuccessMultipleMappings(self):
        """Test multiple mappings do not influence each others correctness."""
        mapper = Mapper([self.VALID_MAPPING_PLAIN, self.VALID_MAPPING_NESTED])

        self.testPlainMapSuccess(mapper)
        self.testNestedMapSuccess(mapper)

    def testFailureUnexpectedContent(self):
        """Test empty output on a non-matching message."""
        mapper = Mapper([self.VALID_MAPPING_PLAIN, self.VALID_MAPPING_NESTED])

        self.assertIsNone(mapper.transform("no object"))
        self.assertIsNone(mapper.transform([]))
        self.assertIsNone(mapper.transform({}))
        self.assertIsNone(mapper.transform({"some": "object", "no": "mapping"}))

        plain_broken = deepcopy(self.VALID_INPUT_PLAIN)
        del plain_broken["timestamp"]
        self.assertIsNone(mapper.transform(plain_broken))

        nested_broken = deepcopy(self.VALID_INPUT_NESTED)
        del nested_broken["nested"]["deeper"]["ipv6"]
        self.assertIsNone(mapper.transform(nested_broken))

    def testFailureWithBrokerUnconformData(self):
        """Test empty output when passed arguments are not convertable to broker conform types ."""

        mapper = Mapper([self.VALID_MAPPING_PLAIN])

        broken = deepcopy(self.VALID_INPUT_PLAIN)
        broken["timestamp"] = "asdkfasdf"
        self.assertIsNone(mapper.transform(broken))

        broken = deepcopy(self.VALID_INPUT_PLAIN)
        broken["ipv4"] = "127.0.0.999"
        self.assertIsNone(mapper.transform(broken))

        broken = deepcopy(self.VALID_INPUT_PLAIN)
        broken["ipv6"] = "2001:0:509c:564e:34ae:3a9a:3f57:fd91:9999"
        self.assertIsNone(mapper.transform(broken))

        broken = deepcopy(self.VALID_INPUT_PLAIN)
        broken["port"] = 9999999 # out of range
        self.assertIsNone(mapper.transform(broken))
        broken["port"] = "foo"
        self.assertIsNone(mapper.transform(broken))

        broken = deepcopy(self.VALID_INPUT_PLAIN)
        broken["string"] = {} # cannot be cast to string
        self.assertIsNone(mapper.transform(broken))

        broken = deepcopy(self.VALID_INPUT_PLAIN)
        broken["number"] = "abc"
        self.assertIsNone(mapper.transform(broken))

        broken = deepcopy(self.VALID_INPUT_PLAIN)
        broken["array"] = 123
        self.assertIsNone(mapper.transform(broken))


    def testFailureInvalidConversionFunc(self):
        """Test empty output when a conversion function is invalid."""
        mapping = deepcopy(self.VALID_MAPPING_PLAIN)
        mapping["mapping"]["timestamp"] = "FOOBAR"
        mapper = Mapper([mapping])
        self.assertIsNone(mapper.transform(self.VALID_INPUT_PLAIN))

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,
        format="[ %(asctime)s | %(name)10s | %(levelname)8s ] %(message)s"
    )
    unittest.main()
