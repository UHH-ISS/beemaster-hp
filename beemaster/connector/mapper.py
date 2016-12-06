# -*- coding: utf-8 -*-
"""mapper.py

Provides the Mapper, which maps json input data to Broker messages.
"""
import pybroker as pb
import datetime
import json
import sys


class Mapper(object):

    def __init__(self, mapping):
        """Mapper(mapping)

        :param mapping:     The mapping to use. (type?)
        """
        self.mapping = mapping
        self.type_conversions = {
            'address': self.__map_address,
            'int': self.__map_integer,
            'time_point': self.__map_time_point,
            'string': self.__map_string,
            'port': self.__map_port
        }

    def __map_final_type(self, prop, value, mapped):
        #print "map final", prop, value, mapped
        if isinstance(mapped, dict):
            mapped = mapped.get(prop)
        if not mapped or not isinstance(mapped, str):
            self.__logUnknown(prop, value)
            return
        handler = self.type_conversions.get(mapped)
        if not handler:
            self.__logUnimplemented(prop, value)
            return
        return handler(value)


    def __logUnknown(self, unknownProp, val):
        # TODO: write to a file? put in bro msg?
        print("Have no mapping configured for property '{}' with value '{}'".format(unknownProp, val))

    def __logUnimplemented(self, prop, val):
        # TODO: write to a file? put in bro msg?
        print("No handler implemented for '{}' with value '{}'".format(prop, val))


    def __map_port(self, port):
        # Maps a port
        # TODO: not quite accurate, add protocol correctly.
        return pb.port(port, pb.port.protocol_tcp)

    def __map_address(self, addr):
        return pb.address_from_string(str(addr))

    def __map_integer(self, num):
        return int(num)

    def __map_string(self, string):
        # TODO: does not work.
        # need nul terminated string for C++
        return str(string)

    def __map_time_point(self, time_str):
        # Maps a time
        date = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')

        # This sets the time_point as a double containing the amount of seconds since epoch
        return pb.time_point((date - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0)

    def __traverse_to_end(self, key, child, currMap):
        msgs = []
        if key in currMap:
            currMap = currMap.get(key) # step into
            try:
                new_key = dict(child).iterkeys().next()
                if new_key:
                    new_child = dict(child).get(new_key)
                    if isinstance(new_child, dict):
                        msgs.extend(self.__traverse_to_end(new_key, new_child, currMap))
                    else:
                        for prop, val in child.iteritems():
                            brokerObj = self.__map_final_type(prop, val, currMap)
                            if brokerObj:
                                msgs.append(brokerObj)
                else: # last iteration step befor plain object body is reached
                    print("aww no key", key)
            except ValueError:
                ## cannot convert to dict, found higher level final mapping type.
                brokerObj = self.__map_final_type(key, child, currMap)
                if brokerObj:
                    msgs.append(brokerObj)
        else:
            self.__logUnknown(key, child)
        return msgs

    def transform(self, dioMsg):
        """map(data)
        Maps *data* to the appropriate Broker message.

        :param data:    The data to map. (json)
        :returns:       The corresponding Broker message. (type?)
        """
        # print("Mapper should map", dioMsg)

        message = pb.message()

        event_name = self.mapping['name']
        message.append(pb.data(event_name))

        for key, val in dioMsg.iteritems():
            lst = self.__traverse_to_end(key, val, self.mapping['mapping'])

        for key, val in dioMsg.iteritems():
            brokerMsgs = self.__traverse_to_end(key, val, self.mapping['mapping'])
            for brokerObject in brokerMsgs:
                print("Add converted brokerObject '{}' to message".format(brokerObject))
                if brokerObject:
                    message.append(pb.data(brokerObject))

        return message
