from sender import Sender

import unittest
import pybroker as pb

import logging
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

        sender = Sender(self.master_ip, self.master_port, self.connector_ep, self.topic,
                        self.connector_id)

        status_queue = self.master_mock.incoming_connection_status()
        readable, _, _ = select([status_queue.fd()], [], [], self.SELECT_TIMEOUT)
        self.assertTrue(readable is not None and readable is not [], "Timout of 'select'")
        
        conn_stati = status_queue.want_pop()
        status_count = 0
        for status in conn_stati:
            self.assertEqual(status.peer_name, self.connector_ep)
            self.assertEqual(status.status, pb.incoming_connection_status.tag_established)
            status_count += 1

        self.assertEqual(status_count, 1)

    def testSuccessSlaveLookupOnInit(self):
        """ Test successful lookup of Bro-Slave instance during sender init """
        self.assertTrue(self.master_listening)
        self.master_store.clear()

        balance_to = "bro-slave"
        self.master_store.insert(pb.data(self.connector_id), pb.data(balance_to))

        sender = Sender(self.master_ip, self.master_port, self.connector_ep, self.topic,
                        self.connector_id)
        
        # force wait for this test
        self.master_mock.incoming_connection_status().need_pop()
        
        # do test slave lookup on init
        self.assertEqual(sender.current_slave, balance_to)


    def testSuccessSlaveLookupOnSend(self):
        """ Test successful (re-)lookup of Bro-Slave instance during sender send """
        self.assertTrue(self.master_listening)
        self.master_store.clear()

        sender = Sender(self.master_ip, self.master_port, self.connector_ep, self.topic,
                        self.connector_id)

        # verify no initial peering took place
        self.assertEqual(sender.current_slave, None)

        balance_to = "bro-slave"
        self.master_store.insert(pb.data(self.connector_id), pb.data(balance_to))

        sleep(0.1) # time for the update of the shared data 
        msg = pb.message()
        msg.append(pb.data(self.topic))
        msg.append(pb.data("MESSAGE"))

        sender.send(msg)

        # do test slave lookup during send
        self.assertEqual(sender.current_slave, balance_to)

if __name__ == '__main__':
    logging.basicConfig(
        # TODO add/set log file
        # TODO adjust time format
        # TODO add log settings to config
        # TODO vary use of log-levels!
        level=logging.DEBUG,
        format="[ %(asctime)s | %(name)10s | %(levelname)8s ] %(message)s"
    )
    unittest.main()
