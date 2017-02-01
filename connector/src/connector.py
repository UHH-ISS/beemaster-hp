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
from __future__ import with_statement

from receiver import Receiver
from mapper import Mapper
from sender import Sender

from argparse import ArgumentParser
import logging
import os.path
from os import walk
import platform
import sys
import yaml


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
            "endpoint_prefix": "beemaster-connector-"
        },
        "connector_id": platform.uname()[1],
        "logging": {
            "file": "stderr",
            "level": "ERROR",
            # as in https://docs.python.org/2.7/library/time.html#time.strftime
            # "datefmt": "%Y-%m-%d %H:%M:%S",  # %f is no py2 feature -.-'
            # None results default format
            "datefmt": None,
            # as in https://docs.python.org/2.7/library/
            #           logging.html#logrecord-attributes
            "format":
                "[ %(asctime)s | %(name)10s | %(levelname)8s ] %(message)s"
        }
    }

    def __init__(self, data=None, default=None):
        """Create the ConnConfig with the read data.

        :param data:    The data to fill in.
        """
        super(ConnConfig, self).__init__()

        # set default values (currently this causes way to much calls into
        # .update, but as we do not do this more than once per run, it should
        # be ok).
        self.default = default
        if default is None:
            self.default = self.DEFAULT_CONFIG
        self.update(self.default)

        if data is not None:
            self.update(data)

    def update(self, ndict):
        """Update the current dict with the new one."""
        for k, v in ndict.iteritems():
            if isinstance(v, dict):
                v = ConnConfig(v, self.default[k])
            self[k] = v

    def __getattr__(self, item):
        """Get the appropriate attribute."""
        # http://stackoverflow.com/a/2405617/2395605
        if item in self:
            return self[item]
        return AttributeError


class Connector(object):
    """The Connector

    See module description for more context.
    """

    REQUIRED_KEYS = {"name", "mapping", "message"}
    RECEIVER_NAME = "bm-connector"

    def __init__(self, config=None):
        """Initialise the Connector and starts to listen to incoming messages.

        :param config:      Configuration to use (default config if None).
        """
        self.log = logging.getLogger(self.__class__.__name__)

        if config is None:
            config = ConnConfig()
            self.log.info("Falling back to default configuration.")

        # errors up to here are allowed to terminate the program

        mappings = self._read_mappings(config.mappings)
        self.mapper = Mapper(mappings)
        self.log.debug("Mappings read.")

        self.sender = Sender(config.send.address, config.send.port,
                             config.broker.endpoint_prefix +
                             config.connector_id,
                             config.broker.topic,
                             config.connector_id)
        self.log.info("Sender created.")

        self.receiver = Receiver(self.RECEIVER_NAME,
                                 config.listen.address, config.listen.port)
        self.log.info("Receiver created.")
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
                        self.log.error(
                            "Missing key '{}' in file '{}'. Ignoring."
                            .format(e.args[0], filepath))
                    except Exception:
                        # TODO find correct exception types.
                        self.log.error(
                            "Failed to read mapping in '{}'. Ignoring."
                            .format(filepath))
        return mappings

    def handle_receive(self, message):
        """Handle message via mapping.

        :param message:     The message to map and send. (json)
        """
        mapped = self.mapper.transform(message)
        if mapped:
            self.log.info("Mapped message is '{}'.".format(mapped))
            self.sender.send(mapped)


def main():
    """Run the connector.

    Execute the connector with command line arguments and/or a configuration
    file.
    """
    ap = ArgumentParser(description="""The Connector takes JSON messages via HTTP
                        (mainly from a Honeypot), maps them to a Broker
                        message, and sends them off to the specified
                        destination. Mapping definitions have to be custom
                        written for each input (see mappings/dionaea for
                        examples).""")

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
    ap.add_argument('--endpoint_prefix', metavar="name",
                    help="Name for the broker endpoint_prefix.")
    # id
    ap.add_argument('--id', metavar="connector_id",
                    help="This connector's unique id.")
    # logging
    ap.add_argument('--log-file', metavar="file",
                    help="The file to log to. 'stderr' and 'stdout' work as "
                    "special names for standard-error and -out respectively.")
    ap.add_argument('--log-level', metavar="level",
                    # FATAL == CRITICAL; WARN == WARNING
                    # Cannot misuse 'type', as file-read configs would not be
                    # converted.
                    choices={'INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'},
                    help="Set the log-level.")
    ap.add_argument('--log-format', metavar="format",
                    help="Set the logging format. See the python docs for more"
                    " information on this.")
    ap.add_argument('--log-datefmt', metavar="format",
                    help="Set the date/time format to use for the logging "
                    "'asctime' placeholder. Python's strftime format is used.")

    # the config file
    ap.add_argument("config", nargs="?", metavar="file",
                    help="Configuration-file to use.")

    # parse arguments
    args = ap.parse_args()

    config = ConnConfig()

    # update with config-values
    if args.config:
        with open(args.config, "r") as conf:
            config.update(yaml.load(conf))

    # update config with settings
    argmap = {'laddr': ['listen', 'address'],
              'lport': ['listen', 'port'],
              'saddr': ['send', 'address'],
              'sport': ['send', 'port'],
              'mappings': ['mappings'],
              'topic': ['broker', 'topic'],
              'endpoint_prefix': ['broker', 'endpoint_prefix'],
              'id': ['connector_id'],
              'log_file': ['logging', 'file'],
              'log_level': ['logging', 'level'],
              'log_format': ['logging', 'format'],
              'log_datefmt': ['logging', 'datefmt']}
    for argument, value in vars(args).iteritems():
        if argument not in argmap or value is None:
            continue
        vals = argmap[argument]
        c = config
        for v in vals[:-1]:
            c = c[v]
        c[vals[-1]] = value

    # set up logging
    logging_dict = {
        'level': getattr(logging, config.logging.level),
        'datefmt': config.logging.datefmt,
        'format': config.logging.format
    }
    if config.logging.file in {'stderr', 'stdout'}:
        logging_dict['stream'] = getattr(sys, config.logging.file)
    else:
        logging_dict['filename'] = config.logging.file
    logging.basicConfig(**logging_dict)
    logging.debug("Logging configured.")

    # start!
    Connector(config)


if __name__ == '__main__':
    main()
