# -*- coding: utf-8 -*-
"""sender.py

Provides the Sender, which wraps Broker to send messages to the associated
communication partner.
"""
from __future__ import unicode_literals

import pybroker as pb
import logging


class Sender(object):
    """The sender.

    Sends Broker messages to an Broker endpoint.
    """

    def __init__(self, address, port, brokerEndpointName, brokerTopic,
                 connectorID):
        """Sender(address, port)

        Initialises the Sender. The address/port are used to peer to the
        corresponding Broker partner.

        :param address:            The address to send to. (str)
        :param port:               The port to send to. (int)
        :param brokerEndpointName: The broker endpoint name to send to. (str)
        :param brokerTopic:        The broker topic to send to. (str)
        :param connectorID:        The connector ID. (str)
        """
        logger = logging.getLogger(self.__class__.__name__)
        self.log = logger.debug

        self.brokerTopic = brokerTopic
        self.connectorID = connectorID
        # TODO: expansion version 1: add service discovery
        self.dioEp = pb.endpoint(brokerEndpointName)
        # Peer with broker endpoint (has to listen to us to receive messages)
        self.dioEp.peer(address, port)

        # TODO check, whether connection has been established.
        # Seems like Broker handles re-peering itself. So when no connection is
        # available, it annoys you with messages and later on reconnects with
        # the other side.

        # TODO: in the future:
        # provide a channel to accept commands (change config,
        # deactivate file logging etc.)
        # self.broEp.listen(9999, "127.0.0.1") #needs also a queue

    def send(self, msg):
        """Send the Broker message to the peer.

        :param msg:        The message to be sent. (Broker message)
        """
        # TODO #86 recheck connection?! retry until connection re-established and
        #      then resend message
        msg.append(pb.data(self.connectorID))
        self.log("Going to send '{}'.".format(msg))
        self.dioEp.send(self.brokerTopic, msg)
