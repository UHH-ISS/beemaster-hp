# -*- coding: utf-8 -*-
"""mapper.py

Provides the Mapper, which maps json input data to Broker messages.
"""
import json
import ConfigParser
from pybroker import *
import datetime

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
            if (self.parser.has_option(section, 'type') and self.parser.has_option(section, 'name') and self.parser.has_option(section, 'arg0')):
                type = self.parser.get(section, 'type')
                #Port types need 2 arguments
                if (type == 'port'):
                    if(not self.parser.has_option(section, 'arg1')):
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
        Maps *data* to the appropriate Broker message.

        :param data:    The data to map. (json)
        :returns:       The corresponding Broker message. (type?)
        """
        print("Mapper should map", pData)

        mapped = {}
        keys = self.flatten(pData)


        #Go through every section in the mapping file
        sectionlist = self.parser.sections()
        for section in sectionlist:
            type = self.parser.get(section, 'type')

            #It's a port
            if(type == 'port'):
                protocol = self.parser.get(section, 'arg1')

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
                a = address_from_string(str(keys[self.parser.get(section, 'arg0')]))
                mapped[self.parser.get(section, 'name')] = a

            #It's an integer
            elif(type == 'int'):
                mapped[self.parser.get(section, 'name')] = self.parser.get(section, 'arg0')

            #It's a time point
            elif(type == 'time_point'):
                date = datetime.datetime.strptime(keys['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
                timestamp = time_point((date - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0)
                mapped[self.parser.get(section, 'name')] = timestamp



        return mapped