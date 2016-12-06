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
from receiver import Receiver
from mapper import Mapper
from sender import Sender
import yaml


class Connector(object):
    def __init__(self):
        """Connector()

        Initialises the Connector and starts to listen to incoming messages.
        """
        stream = open("mapping2.yaml", "r")
        mapperconf = yaml.load(stream)

        self.mapper = Mapper(mapperconf)
        self.sender = Sender('127.0.0.1', 5000)
        self.receiver = Receiver("bm-connector", '0.0.0.0', 8080)
        self.receiver.listen("/", self.handle_receive)

    def handle_receive(self, message):
        """handle_receive(message)

        Handles received messages by mapping them to their specified format and
        sending them out.

        :param message:     The message to map and send. (json)
        """
        # TODO: implement me
        #print "Connector received:", message
        mapped = self.mapper.transform(message)
        print("Mapped message is", mapped)
        print("")
        #success = self.sender.send(mapped)
        #print("Connector did its job? ", success)


if __name__ == '__main__':
    connector = Connector()
