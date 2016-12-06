# -*- coding: utf-8 -*-
"""sender.py

Provides the Sender, which wraps Broker to send messages to the associated
communication partner.
"""
import pybroker as pb

class Sender(object):
    def __init__(self, address, port):
        """Sender(address, port)

        Initialises the Sender. The address/port are used to peer to the
        corresponding Broker partner.

        :param address:     The address to send to. (str)
        :param port:        The port to send to. (int)
        """
        self.address = address # could be removed and used directly
        self.port = port
        #TODO: Move this part into the send method or elsewhere, depending how changing the bro (boker endpoint) should be handled [service discovery]
        self.dioEp = pb.endpoint("dioEp")
        # TODO: check connection status: epStatus = self.dioEp.outgoing_connection_status()
        # peer with broker endpoint. Broker endpoint has to listen to us
        self.dioEp.peer(address, port)

        # TODO: in the future: provide a channel to listen, to accept commands, like deactivate file logging etc.
        #self.broEp.listen(9999, "127.0.0.1") #needs also a queue

    def send(self, msg):
        """send(msg)

        Sends the msg to the peer.

        :param msg:        The message to be sent. (Broker message)
        :returns:           True if message was successfully sent.
        """
        print("Sender should send '{}'' to {}:{}"
              .format(msg, self.address, self.port))
        #TODO: make topic more dynamic? dionaea-ID? Or send id with the broker message?
        self.dioEp.send("honeypot/dionaea/", msg)

        return True #TODO: Is a check possible (message sent & received)? Perhaps by using connection status?
