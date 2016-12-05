# -*- coding: utf-8 -*-
"""mapper.py

Provides the Mapper, which maps json input data to Broker messages.
"""
import json
import ConfigParser
import pybroker as pb
import datetime

class Mapper(object):
    def flatten(self, pData):
        # Flattens the JSON file recursively so nested parts can be easily accessed

        ret = {}
        for keys in pData.keys():
            if (isinstance(pData[keys], dict)):

                recursive = self.flatten(pData[keys])
                for element in recursive.keys():
                    ret[keys + "/" + element] = recursive[element]
            else:
                ret[keys] = pData[keys]
        return ret

    def mapPort(self, section, keys):
        # Maps a port

        portProtocol = self.protocols[keys[section['arg1']]]
        portNumber = keys[section['arg0']]

        p = pb.port(portNumber, portProtocol)
        return p

    def mapAddress(self, section, keys):
        # Maps an address (IP, not sure if host names are supported but they should be)
        a = pb.address_from_string(str(keys[section['arg0']]))
        return a

    def mapInteger(self, section, keys):
        # Maps an integer
        i = int(keys[section['arg0']])
        return i

    def mapTimePoint(self, section, keys):
        # Maps a time
        date = datetime.datetime.strptime(keys[section['arg0']], '%Y-%m-%dT%H:%M:%S.%f')

        # This sets the time_point as a double containing the amount of seconds since epoch
        timestamp = pb.time_point((date - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0)
        return timestamp

    def __init__(self, mapping):
        """Mapper(mapping)

        :param mapping:     The mapping to use. (type?)
        """
        
        self.dictionary = mapping
        self.typedict = {'port': self.mapPort, 'address': self.mapAddress, 'int': self.mapInteger, 'time_point': self.mapTimePoint}

        for key in self.dictionary:
            section = self.dictionary[key]

            # Check if the section is valid. Type, name and at least one argument are always required
            if ('type' in section and 'name' in section and 'arg0' in section):
                brokertype = section['type']
                
                #Port types need 2 arguments
                if (brokertype == 'port'):
                    if(not 'arg1' in section):
                        raise ValueError('Invalid section: ' + key + '. You need 2 arguments (Port number and protocol)')
            else:
                raise ValueError('Invalid section: ' + key + '. Type, name or arg0 missing')

        #save all the transport protocols in a dict
        self.protocols = {'tcp': pb.port.protocol_tcp, 'udp': pb.port.protocol_udp, 'icmp': pb.port.protocol_icmp, 'unknown': pb.port.protocol_unknown}


    def transform(self, pData):
        """map(data)
        Maps *data* to the appropriate Broker message.

        :param data:    The data to map. (json)
        :returns:       The corresponding Broker message. (type?)
        """
        print("Mapper should map", pData)

        keys = self.flatten(pData)
        print(keys)

        message = pb.message()
        #Go through every section in the mapper dictionary
        for key in self.dictionary:

            section = self.dictionary[key]


            brokerObject = self.typedict[section['type']](section, keys)

            message.append(pb.data(brokerObject))

        return message