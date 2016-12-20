#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connector.py

Provides the main class (of) the Connector. This provides the entry-point to
the connector, enables receiving, mapping and sending of messages.

Messages are received via http (default: 0.0.0.0:8080) and sent via broker to
the peered Bro-instance. The incoming messages are mapped via a matching
mapping to be properly processed on the other side.

The module can be executed directly.
"""
from __future__ import unicode_literals, with_statement

from receiver import Receiver
from mapper import Mapper
from sender import Sender
from argparse import ArgumentParser
import os.path
from os import walk
import logging
import yaml

logging.basicConfig(
    # TODO add/set log file
    # TODO adjust time format
    # TODO add log settings to config
    # TODO vary use of log-levels!
    level=logging.DEBUG,
    format="[ %(asctime)s | %(name)10s | %(levelname)8s ] %(message)s"
)

DEFAULT_CONFIG_FILE = 'config.yaml'


class ConnConfig(dict):
    """Connection configuration.

    Provides a proper (default) configuration access as described in
    iss/mp-ids#85.
    """

    DEFAULT_CONFIG = {
        "listen": {
            "address": "0.0.0.0",
            "port": 8080
        },
        "send": {
            "address": "127.0.0.1",
            "port": 5000
        },
        "mappings": "mappings",
        "broker": {
            "topic": "honeypot/dionaea/",
            "endpoint": "dioEp"
        }
    }

    def __init__(self, data=None, is_root=True):
        """Create the ConnConfig with the read data.

        :param data:    The data to fill in.
        """
        super(ConnConfig, self).__init__()
        if is_root:
            self.update(self.DEFAULT_CONFIG)

        # TODO build config checks in here?
        if data is not None:
            self.update(data)

    def update(self, ndict):
        """Update the current dict with the new one."""
        for k, v in ndict.iteritems():
            if isinstance(v, dict):
                v = ConnConfig(v, False)
            self[k] = v

    def __getattr__(self, item):
        """Get the appropriate attribute."""
        # http://stackoverflow.com/a/2405617/2395605
        if item in self:
            return self[item]
        return AttributeError   # TODO check, whether this really works!


class Connector(object):
    """The Connector

    See module description for more context.
    """

    REQUIRED_KEYS = {"name", "mapping", "message"}

    def __init__(self, config=None):
        """Initialise the Connector and starts to listen to incoming messages.

        :param config:      Configuration to use (default config if None).
        """
        # TODO default value shouldn't be hard wired, should it?

        logger = logging.getLogger(self.__class__.__name__)
        self.log = logger.info

        if config is None:
            config = ConnConfig()
            self.log("Falling back to default configuration.")

        # errors up to here are allowed to terminate the program

        mappings = self._read_mappings(config.mappings)
        self.mapper = Mapper(mappings)
        self.log("Mappings read.")

        self.sender = Sender(config.send.address, config.send.port,
                             config.broker.endpoint, config.broker.topic)
        self.log("Sender created.")

        # TODO value should not be const here.
        self.receiver = Receiver("bm-connector",
                                 config.listen.address, config.listen.port)
        self.log("Receiver created.")
        self.receiver.listen("/", self.handle_receive)

    def _read_mappings(self, location):
        """Read the mappings into a list of dictionaries."""
        # os/fs errors here are allowed to terminate the program
        # yaml parse errors should not crash but log
        mappings = []
        for root, _, files in walk(location):
            for f in files:
                filepath = os.path.join(root, f)
                with open(filepath, "r") as fd:
                    # TODO extract the below block?
                    try:
                        mp = yaml.load(fd)
                        for i in self.REQUIRED_KEYS:
                            if i not in mp:
                                raise LookupError(i)
                        mappings.append(mp)
                    except LookupError as e:
                        self.log("Missing key '{}' in file '{}'. Ignoring."
                                 .format(e.args[0], filepath))
                    except Exception:
                        # TODO find correct exception types.
                        self.log("Failed to read mapping in '{}'. Ignoring."
                                 .format(filepath))
        return mappings

    def handle_receive(self, message):
        """Handle message via mapping.

        :param message:     The message to map and send. (json)
        """
        # TODO: implement me
        # print "Connector received:", message
        mapped = self.mapper.transform(message)
        self.log("Mapped message is '{}'.".format(mapped))
        if(mapped):
            self.sender.send(mapped)


def main():
    """Parse given arguments"""
    config = ConnConfig()
    ap = ArgumentParser(description="""The Connector takes messages via http
                        (mainly from a Honeypot), maps them to a Broker Message
                        and sends them off to the specified destination.
                        Mapping definitions have to be custom written for each
                        input (see mappings/dionaea for examples).
                        """)

    # listen
    ap.add_argument('--laddr', metavar="address",
                    help="Address to listen on.")
    ap.add_argument('--lport', metavar="port",
                    type=int,
                    help="Port to listen on.")
    # send
    ap.add_argument('--saddr', metavar="address",
                    help="Address to send to.")
    ap.add_argument('--sport', metavar="port",
                    type=int,
                    help="Port to send to.")
    # mappings
    ap.add_argument('--mappings', metavar="directory",
                    help="Directory to look for mappings.")
    # broker
    ap.add_argument('--topic', metavar="topic",
                    help="Topic for sent messages.")
    ap.add_argument('--endpoint', metavar="name",
                    help="Name for the broker endpoint.")

    # the config file
    ap.add_argument("config", nargs="?", metavar="file",
                    default=DEFAULT_CONFIG_FILE,
                    help="Configuration-file to use.")

    # parse arguments
    args = ap.parse_args()

    # update with config-values
    with open(args.config, "r") as conf:
        config.update(yaml.load(conf))

    # update config with settings
    argmap = {'laddr': ['listen', 'address'],
              'lport': ['listen', 'port'],
              'saddr': ['send', 'address'],
              'sport': ['send', 'port'],
              'mappings': ['mappings'],
              'topic': ['broker', 'topic'],
              'endpoint': ['broker', 'endpoint']}
    # TODO could be done nicer...
    for argument, value in vars(args).iteritems():
        if argument not in argmap:
            continue
        if value is None:
            continue
        vals = argmap[argument]
        c = config
        for v in vals[:-1]:
            c = c[v]
        c[vals[-1]] = value

    Connector(config)


if __name__ == '__main__':
    main()
