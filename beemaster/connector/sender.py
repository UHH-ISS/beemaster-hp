# -*- coding: utf-8 -*-
"""sender.py

Provides the Sender, which wraps Broker to send messages to the associated
communication partner.
"""
import pybroker as pb

class Sender(object):
    def __init__(self, address, port, brokerEndpointName, brokerTopic):
        """Sender(address, port)

        Initialises the Sender. The address/port are used to peer to the
        corresponding Broker partner.

        :param address:            The address to send to. (str)
        :param port:               The port to send to. (int)
        :param brokerEndpointName: The broker endpoint name to send to. (str)
        :param brokerTopic:        The broker topic to send to. (str)
        """

        self.brokerTopic = brokerTopic
        #TODO: expansion version 1: add service discovery
        self.dioEp = pb.endpoint(brokerEndpointName)
        # peer with broker endpoint. Broker endpoint has to listen to us to receive messages
        self.dioEp.peer(address, port)

        # TODO: in the future: provide a channel to listen, to accept commands, like deactivate file logging etc.
        #self.broEp.listen(9999, "127.0.0.1") #needs also a queue

    def send(self, msg):
        """send(msg)

        Sends the msg to the peer.

        :param msg:        The message to be sent. (Broker message)
        :returns:          None
        """

        self.dioEp.send(self.brokerTopic, msg)

        return
