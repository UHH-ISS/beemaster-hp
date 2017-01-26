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
        self.log = logging.getLogger(self.__class__.__name__)

        self.master_name = "{}:{}".format(master_address, port)
        self.master_status = broker.incoming_connection_status.tag_established

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
        self.connector_to_slave_peering = None
        self.current_slave = self._lookup_and_get_current_slave()
        if self.current_slave:
            self.connector_to_slave_peering = self._peer_connector_to_slave()

        # TODO: provide a channel to accept commands (change config etc.)

    def send(self, msg):
        """Send the Broker message to the peer.

        :param msg: The message to be sent. (Broker message)
        """
        msg.append(broker.data(self.connector_id))
        try:
            self._repeer_connector_to_slave()

            if self.current_slave:
                self.log.info("Sending to {}".format(self.current_slave))
                self.connector_to_slave.send(self.broker_topic, msg)
            else:
                self.log.warn(
                    "Not peered with any slave, falling back to master")
                if self._master_connection_established():
                    self.connector_to_master.send(self.broker_topic, msg)
                else:
                    self.log.warn("Connection to master ({}) not established. "
                                  "Sending failed!".format(self.master_name))
        except Exception, e:
            local_endpoint = self.current_slave or self.master_name
            self.log.error("Error sending data from {} to {}. Exception: {}"
                           .format(self.broker_endpoint, local_endpoint, str(e)
                                   ))

    def _lookup_and_get_current_slave(self):
        """Return the slave bro (name) that should be peered with"""
        current_slave = None
        if self.balanced_slaves:
            try:
                current_slave = self.balanced_slaves.lookup(
                    broker.data(self.broker_endpoint)).data().as_string()
                self.log.debug("Lookup {} returns {}"
                               .format(self.broker_endpoint, current_slave))
            except Exception, e:
                self.log.error(
                    "Error looking up slave on connector '{}'. Error: '{}'"
                        .format(self.broker_endpoint, str(e)))
        return current_slave

    def _peer_connector_to_slave(self):
        """Return the peer"""
        slave_ip = self.current_slave[len("bro-slave-"):].split(":")[0]
        slave_port = self.current_slave[len("bro-slave-"):].split(":")[1]
        return self.connector_to_slave.peer(slave_ip, int(slave_port), 1)

    def _repeer_connector_to_slave(self):
        """Repeer the connector to the slave bro if necessary"""
        current_slave = self._lookup_and_get_current_slave()
        if current_slave != self.current_slave:
            # update the receiver, so repeer
            self.current_slave = current_slave
            if self.current_slave:
                self.log.info("Repeering with {}".format(self.current_slave))
                if self.connector_to_slave_peering:
                    self.connector_to_slave.unpeer(
                        self.connector_to_slave_peering)
                self.connector_to_slave_peering = \
                    self._peer_connector_to_slave()
                sleep(0.1)  # repeering may take a moment, make sure..
            else:
                self.log.warn("No slave peered anymore.")
                self.connector_to_slave.unpeer(self.connector_to_slave_peering)

    def _master_connection_established(self):
        """Return True if connection to master is established."""
        ocs = self.connector_to_master.outgoing_connection_status()
        for m in ocs.want_pop():  # Returns message only on change
            self.master_status = m.status

        return self.master_status == \
            broker.incoming_connection_status.tag_established
