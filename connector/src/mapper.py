# -*- coding: utf-8 -*-
"""mapper.py

Provides the Mapper, which maps json input data to Broker messages.
"""
from __future__ import unicode_literals

import pybroker as pb
from datetime import datetime

import logging
import base64


class Mapper(object):
    """The mapper.

    Maps messages over mappings to broker-messages.
    """

    def __init__(self, mappings):
        """Initialise a new Mapper with the given mappings

        :param mappings:    The mapping to use. (List[Dict])
        """
        # TODO self.log could be put into a inheritable class
        # TODO rework use of log-levels

        logger = logging.getLogger(self.__class__.__name__)
        self.log = logger.info

        self.mappings = sorted(mappings,
                               key=lambda mapping: -len(mapping['message']))

    def _map_final_type(self, prop, value, mapped):
        """Try to map the final property."""
        if isinstance(mapped, dict):
            mapped = mapped.get(prop)
        if not mapped or not isinstance(mapped, str):
            self._logUnknown(prop, value)
            return
        handler = getattr(self, '_map_{}'.format(mapped), None)
        if not handler:
            self._logUnimplemented(prop, value)
            return
        return handler(value)

    def _logUnknown(self, unknownProp, val):
        """Log an unknown item."""
        self.log("No Mapping configured for property '{}' with value '{}'."
                 .format(unknownProp, val))

    def _logUnimplemented(self, prop, val):
        """Log an unimplemented item."""
        self.log("No handler implemented for '{}' with value '{}'".
                 format(prop, val))

    def _map_port_count(self, port):
        """Map a port."""
        p = int(port)
        if 0 <= p <= 65535:
            return p

    def _map_address(self, addr):
        """Map an address."""
        return pb.address_from_string(str(addr))

    def _map_count(self, num):
        """Map a count (uint)."""
        return int(num)

    def _map_string(self, string):
        """Map a string."""
        # need nul terminated string for C++
        return str(string)

    def _map_time_point(self, time_str):
        """Map a time_point."""
        # Maps a time
        date = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')

        # TODO 1jost: Could this be easier? It seems to produce a different
        #      result; would like to know what the difference is.
        # return pb.time_point(time.mktime(date.timetuple()))

        # This sets the time_point as a double containing the amount of seconds
        # since epoch.
        return pb.time_point(
            (date - datetime.utcfromtimestamp(0)).total_seconds())

    def _map_array(self, array):
        """Map an array of strings and encode them in base64"""
        string = ";".join(array)
        string = base64.urlsafe_b64encode(string)
        string = string.replace("=", "'")
        return str(string)

    def _traverse_to_end(self, key, child, currMap, acc=None):
        """Traverse the structure to the end."""
        if acc is None:
            acc = {}

        # key and child represent a property from the received message.
        # currMap is the current (sub-)mapping to be applied.

        if key in currMap:
            currMap = currMap[key]
            if isinstance(child, dict):
                for k, v in child.iteritems():
                    self._traverse_to_end(k, v, currMap, acc)
            else:
                brokerObj = self._map_final_type(key, child, currMap)
                if brokerObj is not None:
                    acc[key] = brokerObj

        return acc

    def transform(self, data):
        """Map *data* to the appropriate Broker message.

        :param data:    The data to map. (json)
        :returns:       The corresponding Broker message. (pybroker.Message)
        """
        self.log("Trying to map '{}'.".format(data))

        for mapping in self.mappings:
            event_name = mapping['name']
            self.log("Using mapping for '{}'.".format(event_name))

            message = pb.message()
            # prepending with event-name for broker
            message.append(pb.data(event_name))

            local_mapping = mapping['mapping']
            # the actual traversion
            try:
                brokerMsg = {k2: v2 for k, v in data.iteritems() for k2, v2
                             in self._traverse_to_end(k, v, local_mapping)
                             .iteritems()}
            except Exception:
                # TODO specify possible exception! maybe even custom ones in
                #      _map_*.
                self.log("Failed to convert message properly. "
                         "Ignoring format.")
                break

            # setting up the final message in desired order
            local_message = mapping['message']
            for item in local_message:
                if item not in brokerMsg:
                    self.log("Invalid message. Format unknown.")
                    break
                broker_item = brokerMsg[item]
                self.log("Add converted brokerObject '{}' to message."
                         .format(broker_item))
                # TODO would be nice to set the message in one step only
                message.append(pb.data(broker_item))
            else:
                return message
        else:
            self.log("No valid mapping found. Discarding message.")
            return
