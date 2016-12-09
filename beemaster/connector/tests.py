import unittest
import pybroker as pb
import datetime
import json
from mapper import Mapper
import yaml

stream = open("mappings/dionaea/connection.yaml", "r")
mapperconf = yaml.load(stream)

class mappings():
    def map_port(self, port):
        # Maps a port
        # TODO: not quite accurate, add protocol correctly.
        return pb.port(port, pb.port.protocol_tcp)


    def map_address(self, addr):
        return pb.address_from_string(str(addr))


    def map_count(self, num):
        return int(num)


    def map_string(self, string):
        # need nul terminated string for C++
        return str(string)


    def map_time_point(self, time_str):
        # Maps a time
        date = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')

        # This sets the time_point as a double containing the amount of seconds since epoch
        return pb.time_point((date - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0)


class TestMapper(unittest.TestCase):

    def testStandard(self):
        mapper = Mapper(mapperconf)
        testmap = mappings()
        testmessage = '{"timestamp": "2016-11-26T22:18:56.281464", "data": {"connection": {"remote_ip": "127.0.0.1", "remote_hostname": "", "id": 3019197952, "protocol": "pcap", "local_port": 4101, "local_ip": "127.0.0.1", "remote_port": 35324, "transport": "tcp"}}, "name": "dionaea", "origin": "dionaea.connection.free"}'
        expectedResult = pb.message()
        expectedResult.append(pb.data(testmap.map_time_point("2016-11-26T22:18:56.281464")))
        expectedResult.append(pb.data(testmap.map_count(3019197952)))
        expectedResult.append(pb.data(testmap.map_address("127.0.0.1")))
        expectedResult.append(pb.data(testmap.map_count("4101")))
        expectedResult.append(pb.data(testmap.map_address("127.0.0.1")))
        expectedResult.append(pb.data(testmap.map_count("35324")))
        expectedResult.append(pb.data(testmap.map_string("tcp")))

        mapResult = mapper.transform(json.loads(testmessage))

        while not expectedResult.empty():
            self.assertEqual(expectedResult.pop(), mapResult.pop())

    def testEmpty(self):
        mapper = Mapper(mapperconf)
        testmessage = '{"origin": "dionaea.connection.link", "timestamp": "2016-12-09T21:11:09.315143", "data": {"parent": {"protocol": "httpd", "local_port": 80, "local_ip": "127.0.0.1", "remote_hostname": "", "remote_port": 0, "id": 140386985909024, "transport": "tcp", "remote_ip": ""}, "child": {"protocol": "httpd", "local_port": 80, "local_ip": "127.0.0.1", "remote_hostname": "", "remote_port": 59268, "id": 140386985908744, "transport": "tcp", "remote_ip": "127.0.0.1"}}, "name": "dionaea"}'

        mapResult = mapper.transform(json.loads(testmessage))

        self.assertIsNone(mapResult)

if __name__ == '__main__':
    unittest.main()






#tests().standardtest()