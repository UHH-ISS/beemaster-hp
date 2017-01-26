# -*- coding: utf-8 -*-
"""sender.py

Provides the Sender, which wraps Broker to send messages to the associated
communication partner.
"""
# The following import _must_ not be made, otherwise some python binding calls
# for broker distributed datastores do not work anymore. The import is left
# commented-out to avoid someone trapping in this issue.
# from __future__ import unicode_literals

import pybroker as broker
import logging
from time import sleep
from select import select


class Sender(object):
    """The sender.

    Sends Broker messages to an Broker endpoint.
    """

    def __init__(self, master_address, port, broker_endpoint, broker_topic,
                 connector_id):
        """Sender(master_address, port)

        Initialises the Sender. The master_address/port are used to peer to the
        corresponding Broker partner.

        :param master_address:     The address/hostname of the master bro
                                   instance. (str)
        :param port:               The port to send to. (int)
        :param broker_endpoint:    The broker endpoint name to use for
                                   connecting to the master. (str)
        :param broker_topic:       The broker topic to send to. (str)
        :param connector_id:       The connector ID. (str)
        """
        logger = logging.getLogger(self.__class__.__name__)
        self.log = logger

        self.broker_topic = broker_topic
        self.broker_endpoint = broker_endpoint
        self.connector_id = connector_id

        self.connector_to_master = broker.endpoint(self.broker_endpoint)
        # Peer with broker endpoint of bro master instance
        self.connector_to_master.peer(master_address, port, 1)

        # dedicated endpoint for sending to slaves
        self.connector_to_slave = broker.endpoint(connector_id)
        # note: "connectors" is the name of the distributed datastore
        self.balanced_slaves = broker.clone_create(self.connector_to_master,
                                                   "connectors", 1)
        self.current_slave = None
        self.connector_to_slave_peering = None

        try:
            if self.balanced_slaves:
                self.current_slave = self.balanced_slaves.lookup(
                    broker.data(self.broker_endpoint)).data().as_string()
                self.log.debug("Lookup {} returns {}"
                               .format(self.broker_endpoint,
                                       self.current_slave))

        except Exception, e:
            self.log.error(
                "Error looking up slave on connector '{}' init. Error: '{}'"
                .format(self.broker_endpoint, str(e)))

        if self.current_slave:
            slave_ip = self.current_slave[len("bro-slave-"):].split(":")[0]
            slave_port = self.current_slave[len("bro-slave-"):].split(":")[1]
            self.connector_to_slave_peering = self.connector_to_slave.peer(
                slave_ip, int(slave_port), 1)

        # TODO: in the future:
        # provide a channel to accept commands (change config,
        # deactivate file logging etc.)

    def send(self, msg):
        """Send the Broker message to the peer.

        :param msg:        The message to be sent. (Broker message)
        """
        msg.append(broker.data(self.connector_id))
        current_slave = None
        try:
            current_slave = self.balanced_slaves.lookup(
                broker.data(self.broker_endpoint)).data().as_string()
            self.log.debug("Looked up slave {}".format(current_slave))
        except Exception, e:
            self.log.error(
                "Error looking up slave on connector '{}' send. Error: '{}'"
                .format(self.broker_endpoint, str(e)))
        try:
            if current_slave != self.current_slave:
                # update the receiver, so repeer
                self.current_slave = current_slave
                if self.current_slave:
                    self.log.info("Repeering with {}"
                                  .format(self.current_slave))
                    if self.connector_to_slave_peering:
                        self.connector_to_slave.unpeer(
                            self.connector_to_slave_peering)
                    slave_ip =\
                        self.current_slave[len("bro-slave-"):].split(":")[0]
                    slave_port =\
                        self.current_slave[len("bro-slave-"):].split(":")[1]
                    self.connector_to_slave_peering =\
                        self.connector_to_slave.peer(slave_ip, int(slave_port),
                                                     1)
                    sleep(0.1)  # repeering may take a moment, make sure..
                else:
                    self.log.warn("No slave peered anymore.")
                    self.connector_to_slave.unpeer(
                        self.connector_to_slave_peering)

            if self.current_slave:
                self.log.info("Sending to {}".format(self.current_slave))
                self.connector_to_slave.send(self.broker_topic, msg)
            else:
                self.log.warn(
                    "Not peered with any slave, falling back to master")
                if self.bro_connection_established(self.connector_to_master):
                    self.connector_to_master.send(self.broker_topic, msg)
                else:
                    self.log.warn("Connection to master not established. "
                                  "Sending failed!")
                    # TODO: Queue of not sent messages.
        except Exception, e:
            self.log.error("Error sending data from {} to {}. Exception: {}"
                           .format(self.broker_endpoint,
                                   self.current_slave or "bro-master", str(e)))

    def bro_connection_established(self, broker_endpoint):
        """Return False if no connection to other endpoint is established"""
        status = 0  # status == 0 -> connection established
        ocs = broker_endpoint.outgoing_connection_status()
        # TODO: select times out after the first time
        # status is set to = 0, because if no connection is established it
        # *always* gets an response immediately, and that is the one we need
        s, _, __ = select([ocs.fd()], [], [], 0.001)
        self.log.debug("Timout of 'select': {}".format(s))
        for m in ocs.want_pop():
            status = m.status
            self.log.info(
                "peer_name: {}; status: {} (status should be: {})"
                    .format(m.peer_name, m.status,
                            broker.incoming_connection_status.tag_established))

        return status == broker.incoming_connection_status.tag_established
