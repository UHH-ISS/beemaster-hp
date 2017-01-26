# -*- coding: utf-8 -*-
"""receiver.py

Provides the Receiver, which listens to the given address and reacts on data.
The method :meth:`Receiver.on_data` is called upon a valid json message. Start
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
        self.log = logging.getLogger(self.__class__.__name__)

        super(Receiver, self).__init__(name)

        self.name = name
        self.address = address
        self.port = port
        self.on_data = None

    def listen(self, route, on_data):
        """Listen on *route* and call *on_data*.

        :param route:       The path to listen on. (str)
        :param on_data:     The callback function. (func(json))
        """
        self.on_data = on_data

        self.route(route, methods=['POST'])(self.__handle_post)
        self.run(host=self.address, port=self.port, debug=False)

    def __handle_post(self):
        if 'application/json' in request.headers.get('Content-Type'):
            try:
                data = request.json
                # TODO: weak check:
                data = json.loads(json.dumps(data))

                self.log.debug(data)
                self.on_data(data)
            except Exception:
                return Response('Bad Request', 400)

            return Response('OK', 200)
        return Response('Unsupported Media Type', 415)
