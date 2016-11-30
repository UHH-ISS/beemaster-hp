# -*- coding: utf-8 -*-
"""sender.py

Provides the Sender, which wraps Broker to send messages to the associated
communication partner.
"""


class Sender(object):
    def __init__(self, address, port):
        """Sender(address, port)

        Initialises the Sender. The address/port are used to peer to the
        corresponding Broker partner.

        :param address:     The address to send to. (str)
        :param port:        The port to send to. (int)
        """
        self.address = address
        self.port = port

    def send(self, data):
        """send(data)

        Sends the data to the peer.

        :param data:        The data to be sent. (Broker message)
        :returns:           True if message was successfully sent.
        """
        print("Sender should send '{}'' to {}:{}"
              .format(data, self.address, self.port))
        return True
