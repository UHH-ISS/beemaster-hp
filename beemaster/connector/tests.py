import unittest
import pybroker as pb
from mapper import Mapper
import yaml

stream = open("mappings/dionaea/connection.yaml", "r")
mapperconf = yaml.load(stream)
mapper = Mapper(mapperconf)


testmessage = "{u'origin': u'dionaea.connection.free', u'timestamp': u'2016-12-08T20:08:14.243187', u'data': {u'connection': {u'protocol': u'httpd', u'local_port': 80, u'local_ip': u'127.0.0.1', u'remote_hostname': u'', u'remote_port': 45710, u'id': 140386883066176, u'transport': u'tcp', u'remote_ip': u'127.0.0.1'}}, u'name': u'dionaea'}"
result = pb.message
result.append(pb.data(mapper))
unittest.TestCase.assertEqual(mapper.transform())