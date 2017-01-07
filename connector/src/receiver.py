# -*- coding: utf-8 -*-
"""receiver.py

Provides the Receiver, which listens to the given address and reacts on data.
The method :meth:`Receiver.onData` is called upon a valid json message. Start
it by calling :func:`~Receiver.listen`.

This implementation uses Flask (http://flask.pocoo.org/)!
"""
from flask import Flask, request, json, Response
# ATTENTION: The imported json is a custom implementation of the internal json
#            module. https://github.com/pallets/flask/blob/master/flask/json.py

import logging


class Receiver(Flask):
    """Receiver

    See module description.
    """

    def __init__(self, name, address, port):
        """Receiver(name, address, port)

        Instantiates the Receiver. Start the service via
        :func:`~Receiver.listen`.

        :param name:        Name of the receiver. (str)
        :param address:     Address to listen on. (str)
        :param port:        Port to listen on. (int)
        """
        logger = logging.getLogger(self.__class__.__name__)
        self.log = logger.info

        super(Receiver, self).__init__(name)

        self.name = name
        self.address = address
        self.port = port
        self.onData = self.logToFile    # fallback

    def logToFile(self, text):
        """OBSOLETE

        Log to a file (log.txt).

        :param text:    The data received.
        """
        # TODO adjust for logging only!
        with open('./log.txt', 'a+') as log:
            json.dump(text, log)
            log.write('\n')

    def listen(self, route, onData):
        """Listen on *route* and call *onData*.

        :param route:       The path to listen on. (str)
        :param onData:      The callback function. (func(json))
        """
        self.onData = onData

        self.route(route, methods=['POST'])(self.__handle_post)
        self.run(host=self.address, port=self.port, debug=False)

    def __handle_post(self):
        if 'application/json' in request.headers.get('Content-Type'):
            try:
                data = request.json
                # TODO weak check:
                data = json.loads(json.dumps(data))

                self.log(data)
                self.onData(data)
            except Exception:
                return Response('Bad Request', 400)

            return Response('OK', 200)
        return Response('Unsupported Media Type', 415)
