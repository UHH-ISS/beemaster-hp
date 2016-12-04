# -*- coding: utf-8 -*-
"""mapper.py

Provides the Mapper, which maps json input data to Broker messages.
"""
import json
import ConfigParser
from pybroker import *

class Mapper(object):
    def __init__(self, mapping):
        """Mapper(mapping)

        :param mapping:     The mapping to use. (type?)
        """
        self.mapping = mapping
        self.parser = ConfigParser.ConfigParser()
        self.parser.read('mapping.cfg')

        sectionlist = self.parser.sections()
        for section in sectionlist:
            # Check if the section is valid. Type, name and at least one argument are always required
            if (self.parser.has_option('type') and self.parser.has_option('name') and self.parser.has_option('arg0')):
                type = self.parser.get(section, 'type')
                #Port types need 2 arguments
                if (type == 'port'):
                    if(not self.parser.has_option('arg1')):
                        raise ValueError('Invalid section: ' + section + '. You need 2 arguments (Port number and protocol)')
            else:
                raise ValueError('Invalid section: ' + section + '. Type, name or arg0 missing')

    def flatten(self, pData):

        ret = {}
        for keys in pData.keys():
            if (isinstance(pData[keys], dict)):
                ret.update(self.flatten(pData[keys]))
            else:
                ret[keys] = pData[keys]
        return ret

    def map(self, pData):
        """map(data)
#'{"timestamp": "2016-11-26T22:18:56.281464", "data": {"connection": {"remote_ip": "127.0.0.1", "remote_hostname": "", "id": 3019197952, "protocol": "pcap", "local_port": 4101, "local_ip": "127.0.0.1", "remote_port": 35324, "transport": "tcp"}}, "name": "dionaea", "origin": "dionaea.connection.free"}'
        Maps *data* to the appropriate Broker message.

        :param data:    The data to map. (json)
        :returns:       The corresponding Broker message. (type?)
        """
        print("Mapper should map", pData)

        mapped = {}
        keys = self.flatten(pData)
        #p = port(999,port.protocol_tcp)
        #print(port.number(p))
        #a = address_from_string("127.0.0.1")
        #print(address.is_v6(a))

        #Go through every section in the mapping file
        sectionlist = self.parser.sections()
        for section in sectionlist:
            type = self.parser.get(section, 'type')

            #It's a port
            if(type == 'port'):
                protocol = self.parser.get('arg1')

                if(keys[protocol] == 'tcp'):
                    protocol = port.protocol_tcp

                elif(keys[protocol] == 'udp'):
                    protocol = port.protocol_udp

                #Not sure if we need this but I'll include it anyway
                elif (keys[protocol] == 'icmp'):
                    protocol = port.protocol_icmp

                #Protocol unknown? wtf
                else:
                    protocol = port.protocol_unknown


                p = port(keys[self.parser.get(section, 'arg0')], protocol)
                mapped[self.parser.get(section, 'name')] = p

            #It's an IP or host address
            elif(type == 'address'):
                a = address_from_string(keys[self.parser.get(section, 'arg0')])
                mapped[self.parser.get(section, 'name')] = a

            #It's an integer
            elif(type == 'int'):
                mapped[self.parser.get(section, 'name')] = self.parser.get(section, 'arg0')


        return "xxx-some-broker-msg-xxx"