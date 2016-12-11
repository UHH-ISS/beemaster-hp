# -*- coding: utf-8 -*-
"""sender.py

Provides the Sender, which wraps Broker to send messages to the associated
communication partner.
"""
import pybroker as pb

import logging


class Sender(object):
    """The sender.

    Sends Broker messages to an Broker endpoint.
    """

    def __init__(self, address, port, brokerEndpointName, brokerTopic):
        """Sender(address, port)

        Initialises the Sender. The address/port are used to peer to the
        corresponding Broker partner.

        :param address:            The address to send to. (str)
        :param port:               The port to send to. (int)
        :param brokerEndpointName: The broker endpoint name to send to. (str)
        :param brokerTopic:        The broker topic to send to. (str)
        """
        logger = logging.getLogger(self.__class__.__name__)
        self.log = logger.debug

        self.brokerTopic = brokerTopic
        # TODO: expansion version 1: add service discovery
        self.dioEp = pb.endpoint(brokerEndpointName)
        # Peer with broker endpoint (has to listen to us to receive messages)
        self.dioEp.peer(address, port)

        # TODO check, whether connection has been established.

        # TODO: in the future:
        # provide a channel to accept commands (change config,
        # deactivate file logging etc.)
        # self.broEp.listen(9999, "127.0.0.1") #needs also a queue

    def send(self, msg):
        """Send the Broker message to the peer.

        :param msg:        The message to be sent. (Broker message)
        """
        # TODO recheck connection?! retry until connection re-established
        self.dioEp.send(self.brokerTopic, msg)
