#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_sender

Test the Sender.
"""

from sender import Sender

import unittest
import pybroker as pb

from select import select


class TestSender(unittest.TestCase):
    """TestCases for sender.Sender"""

    topic = "honeypotconnector/unittest"
    ip = "127.0.0.1"
    port = 9765

    TIMEOUT = 5

    def testSuccessPeering(self):
        """Test successful peer"""
        i = 0
        epl = pb.endpoint("listener")
        icsl = epl.incoming_connection_status()

        # To maintain the peering, the Sender needs to exist -> variable
        sender = Sender(self.ip, self.port, "connector", self.topic,    # noqa
                        "unittestSender")
        # true: endpoint is listening
        self.assertTrue(epl.listen(self.port, self.ip))

        s, _, __ = select([icsl.fd()], [], [], self.TIMEOUT)
        self.assertFalse(s is None or s == [], "Timout of 'select'")
        msgs = icsl.want_pop()

        for m in msgs:
            self.assertEqual(m.peer_name, "connector")
            self.assertEqual(m.status,
                             pb.incoming_connection_status.tag_established)
            i += 1

        # Be sure to have exactly one status message
        self.assertEqual(i, 1)

    def testSuccessSend(self):
        """Test sending a message.

        Should not raise an Exception or anything.
        """
        i = 0
        port = self.port + 1
        epname = "unittestSenderSuccess"
        msgcontent = "hi"
        epl = pb.endpoint("listenerSuccess")
        mql = pb.message_queue(self.topic, epl)

        sender = Sender(self.ip, port, "connector", self.topic, epname)
        self.assertTrue(epl.listen(port, self.ip))

        # for some reason the test fails without these two lines of code
        icsl = epl.incoming_connection_status()
        s, _, __ = select([icsl.fd()], [], [], self.TIMEOUT)
        self.assertFalse(s is None or s == [], "Timout of 'select'")

        sender.send(pb.message([pb.data(msgcontent)]))

        s, _, __ = select([mql.fd()], [], [], self.TIMEOUT)
        self.assertFalse(s is None or s == [], "Timout of 'select'")
        msgs = mql.want_pop()

        for m in msgs:
            for d in m:
                i += 1
                if i == 1:
                    self.assertEqual(d.which(), pb.data.tag_string)
                    self.assertEqual(d.as_string(), msgcontent)
                if i == 2:
                    self.assertEqual(d.which(), pb.data.tag_string)
                    self.assertEqual(d.as_string(), epname)

        self.assertEqual(i, 2)

    def testFailureSendInvalidMessage(self):
        """Test sending a message that is a simple string."""
        sender = Sender(self.ip, self.port, "brokerEndpointName",
                        self.topic, "unittestSender")

        with self.assertRaises(AttributeError):
            sender.send("")

    def testFailurePeer(self):
        """Try peering with not existing endpoint:

        - Listen to not existing endpoint (tests Broker actually)
        - Send message to not existing endpoint (test Sender)
          Should not raise an Exception or anything.
        """
        iip = "999.999.999.999"
        epl = pb.endpoint("listener")
        self.assertFalse(epl.listen(self.port, iip))

        sender = Sender(self.ip, self.port, "connector", self.topic,
                        "unittestSender")
        sender.send(pb.message([pb.data("hi")]))
        # TODO: #86 - implement in Sender check, if peer was successful
        # - if message was received by endpoint cannot be checked at this point

    def testFailureInvalidPort(self):
        """Create a Sender with an invalid connection (ip)."""
        with self.assertRaises(NotImplementedError):
            Sender(self.ip, "9999", "brokerEndpointName",
                   self.topic, "connectorID15")

    def testFailureInvalidIp(self):
        """Create a Sender with an invalid connection (port)."""
        with self.assertRaises(NotImplementedError):
            Sender(self.port, self.port, "brokerEndpointName",
                   self.topic, "connectorID15")
            # Broker bindings do not check for valid IPs. Strings are accepted.


if __name__ == '__main__':
    unittest.main()
