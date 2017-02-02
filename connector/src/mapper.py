# -*- coding: utf-8 -*-
"""mapper.py

Provides the Mapper, which maps json input data to Broker messages.
"""
import pybroker as pb
from datetime import datetime

import logging
import re


class Mapper(object):
    """The mapper.

    Maps messages over mappings to broker-messages.
    """

    def __init__(self, mappings):
        """Initialise a new Mapper with the given mappings

        :param mappings:    The mapping to use. (List[Dict])
        """
        self.log = logging.getLogger(self.__class__.__name__)

        self.mappings = sorted(mappings,
                               key=lambda mapping: -len(mapping['message']))

    def _map_final_type(self, prop, value, mapped):
        """Try to map the final property."""
        if isinstance(mapped, dict):
            mapped = mapped.get(prop)
        if not mapped or not isinstance(mapped, str):
            self._log_unknown(prop, value)
            return
        handler = getattr(self, '_map_{}'.format(mapped), None)
        if not handler:
            self._log_unimplemented(prop, value)
            return
        return handler(value)

    def _log_unknown(self, prop, val):
        """Log an unknown item."""
        self.log.info("No Mapping configured for property "
                      "'{}' with value '{}'.".format(prop, val))

    def _log_unimplemented(self, prop, val):
        """Log an unimplemented item."""
        self.log.info("No handler implemented for '{}' with value '{}'"
                      .format(prop, val))

    @staticmethod
    def _map_port_count(port):
        """Map a port."""
        p = int(port)
        if 0 <= p <= 65535:
            return p

    @staticmethod
    def _map_address(addr):
        """Map an address."""
        return pb.address_from_string(str(addr))

    @staticmethod
    def _map_count(num):
        """Map a count (uint)."""
        return int(num)

    @staticmethod
    def _map_string(string):
        """Map a string and replace tabs with normal spaces."""
        # need nul terminated string for C++, also encoding for special chars
        if type(string) is unicode:
            string = str(string.encode('utf8'))
        else:
            string = str(string)
        string = re.sub(r"\s+", ' ', string)
        return string

    @staticmethod
    def _map_time_point(time_str):
        """Map a time_point."""
        date = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')

        # This sets the time_point as a double containing the amount of seconds
        # since epoch.
        return pb.time_point(
            (date - datetime.utcfromtimestamp(0)).total_seconds())

    @staticmethod
    def _map_array(array):
        """Map an array of strings and replace tabs with normal spaces"""
        string = ";".join(array)
        if type(string) is unicode:
            string = str(string.encode('utf8'))
        else:
            string = str(string)
        string = re.sub(r"\s+", ' ', string)
        return string

    def _traverse_to_end(self, key, child, curr_map, acc=None):
        """Traverse the structure to the end."""
        if acc is None:
            acc = {}

        # key and child represent a property from the received message.
        # currMap is the current (sub-)mapping to be applied.

        if key in curr_map:
            curr_map = curr_map[key]
            if isinstance(child, dict):
                for k, v in child.iteritems():
                    self._traverse_to_end(k, v, curr_map, acc)
            else:
                broker_obj = self._map_final_type(key, child, curr_map)
                if broker_obj is not None:
                    acc[key] = broker_obj

        return acc

    def transform(self, data):
        """Map *data* to the appropriate Broker message.

        :param data:    The data to map. (json)
        :returns:       The corresponding Broker message. (pybroker.Message)
        """
        self.log.debug("Trying to map '{}'.".format(data))

        for mapping in self.mappings:
            event_name = mapping['name']
            self.log.debug("Trying mapping for '{}'.".format(event_name))

            local_mapping = mapping['mapping']
            # the actual traversion
            try:
                broker_msg = {k2: v2 for k, v in data.iteritems() for k2, v2
                              in self._traverse_to_end(k, v, local_mapping)
                              .iteritems()}
            except Exception:
                self.log.info("Failed to convert message properly. "
                              "Ignoring format.")
                continue

            self.log.info("Using mapping for '{}'.".format(event_name))
            message = pb.message()
            # prepending with event-name for broker
            message.append(pb.data(event_name))

            # setting up the final message in desired order
            local_message = mapping['message']
            for item in local_message:
                if item not in broker_msg:
                    self.log.debug("Invalid message. Format unknown.")
                    break
                broker_item = broker_msg[item]
                self.log.debug("Add converted brokerObject '{}' to message."
                               .format(broker_item))
                message.append(pb.data(broker_item))
            else:
                return message
        else:
            self.log.warn("No valid mapping found. Discarding message.")
            return
