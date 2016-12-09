#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connector.py

Provides the main class (of) the Connector. This provides the entry-point to
the connector, enables receiving, mapping and sending of messages.

Messages are received via http (default: 0.0.0.0:8080) and sent via broker to
the peered Bro-instance. The incoming messages are mapped via a matching
mapping to be properly processed on the other side.

The module can be executed directly.
"""
from __future__ import print_function

from receiver import Receiver
from mapper import Mapper
from sender import Sender
import yaml
import os.path


class Connector(object):
    def __init__(self):
        """Connector()

        Initialises the Connector and starts to listen to incoming messages.
        """
        # TODO to be made dynamic

        stream = open("config.yaml", "r")
        config = yaml.load(stream)

        if 'mapping' in config and 'sendPort' in config and 'listenPort' in config and 'sendIP' in config:
            stream = open("mappings/" + config['mapping'], "r")
            mapperconf = yaml.load(stream)
            self.mapper = Mapper(mapperconf)
            self.sender = Sender(config['sendIP'], config['sendPort'])
            self.receiver = Receiver("bm-connector", '0.0.0.0', config['listenPort'])
            self.receiver.listen("/", self.handle_receive)
        else:
            raise LookupError('config incomplete')





    def handle_receive(self, message):
        """handle_receive(message)

        Handles received messages by mapping them to their specified format and
        sending them out.

        :param message:     The message to map and send. (json)
        """
        # TODO: implement me
        # print "Connector received:", message
        mapped = self.mapper.transform(message)
        print("Mapped message is", mapped)
        print("")
        #if(message):
            # success = self.sender.send(mapped)
            # print("Connector did its job? ", success)


if __name__ == '__main__':
    connector = Connector()
