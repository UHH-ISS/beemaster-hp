# -*- coding: utf-8 -*-
"""mapper.py

Provides the Mapper, which maps json input data to Broker messages.
"""


class Mapper(object):
    def __init__(self, mapping):
        """Mapper(mapping)

        :param mapping:     The mapping to use. (type?)
        """
        self.mapping = mapping

    def map(self, data):
        """map(data)

        Maps *data* to the appropriate Broker message.

        :param data:    The data to map. (json)
        :returns:       The corresponding Broker message. (type?)
        """
        print("Mapper should map", data)
        return "xxx-some-broker-msg-xxx"
