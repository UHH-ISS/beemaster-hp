#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_sender

Test the Sender.
"""

from __future__ import with_statement

from sender import Sender

import unittest
import pybroker as pb

from time import sleep
from select import select


class TestSender(unittest.TestCase):
    """TestCases for sender.Sender"""

    topic = "honeypotconnector/unittest"
    master_ip = "127.0.0.1"
    master_port = 9765
    connector_id = "test"
    connector_ep = connector_id

    datastore = "connectors"

    # setup for all tests shared
    master_mock = pb.endpoint("master_ep")
    master_listening = master_mock.listen(master_port, master_ip)
    master_store = pb.master_create(master_mock, datastore)

    SELECT_TIMEOUT = 5

    def testSuccessMasterPeering(self):
        """Test successful peer with the Bro-Master instance"""
        self.assertTrue(self.master_listening)

        sender = Sender(self.master_ip, self.master_port, self.connector_ep,
                        self.topic, self.connector_id)

        assert sender is not None

        status_queue = self.master_mock.incoming_connection_status()
        readable, _, _ = select([status_queue.fd()], [], [],
                                self.SELECT_TIMEOUT)

        self.assertTrue(readable is not None and readable is not [],
                        "Timout of 'select'")

        conn_stati = status_queue.want_pop()
        status_count = 0
        for status in conn_stati:
            self.assertEqual(status.peer_name, self.connector_ep)
            self.assertEqual(status.status,
                             pb.incoming_connection_status.tag_established)
            status_count += 1

        self.assertEqual(status_count, 1)

    def testSuccessSlaveLookupOnInit(self):
        """Test successful lookup of Bro-Slave instance during sender init"""
        self.assertTrue(self.master_listening)
        self.master_store.clear()

        balance_to = "bro-slave-127.0.0.1:9999"
        self.master_store.insert(pb.data(self.connector_id),
                                 pb.data(balance_to))

        sender = Sender(self.master_ip, self.master_port, self.connector_ep,
                        self.topic, self.connector_id)

        # force wait for this test
        self.master_mock.incoming_connection_status().need_pop()

        # do test slave lookup on init
        self.assertEqual(sender.current_slave, balance_to)

    def testSuccessSlaveLookupOnSend(self):
        """Test successful (re-)lookup of Bro-Slave during sender send"""
        self.assertTrue(self.master_listening)
        self.master_store.clear()

        sender = Sender(self.master_ip, self.master_port, self.connector_ep,
                        self.topic, self.connector_id)

        # verify no initial peering took place
        self.assertEqual(sender.current_slave, None)

        balance_to = "bro-slave-127.0.0.1:9999"
        self.master_store.insert(pb.data(self.connector_id),
                                 pb.data(balance_to))

        sleep(0.1)  # time for the update of the shared data
        msg = pb.message()
        msg.append(pb.data(self.topic))
        msg.append(pb.data("MESSAGE"))

        sender.send(msg)

        # do test slave lookup during send
        self.assertEqual(sender.current_slave, balance_to)

    def testFailureSendInvalidMessage(self):
        """Test failure sending anything that is not a pybroker::message"""
        other_master_mock = pb.endpoint("other_master_ep")
        other_master_port = 9766
        pb.master_create(other_master_mock, self.datastore)  # avoid block

        self.assertTrue(other_master_mock.listen(other_master_port,
                        self.master_ip))

        sender = Sender(self.master_ip, other_master_port, self.connector_ep,
                        self.topic, self.connector_id)

        with self.assertRaises(AttributeError):
            sender.send("")
        with self.assertRaises(AttributeError):
            sender.send(1)
        with self.assertRaises(AttributeError):
            sender.send(self)

#    def testFailureMasterPeer(self):
#       """Try peering with not existing endpoint"""
#
#       invalid_ip = "999.999.999.999"
#       ep = pb.endpoint("listener")
#       self.assertFalse(ep.listen(self.master_port, invalid_ip))
#       sender = Sender(invalid_ip, 9999, self.connector_ep, self.topic,
#                       self.connector_id)


if __name__ == '__main__':
    unittest.main()
