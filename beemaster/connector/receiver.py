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


class Receiver(Flask):
    def __init__(self, name, address, port):
        """Receiver(name, address, port)

        Instantiates the Receiver. Start the service via
        :func:`~Receiver.listen`.

        :param name:        Name of the receiver. (str)
        :param address:     Address to listen on. (str)
        :param port:        Port to listen on. (int)
        """
        super(Receiver, self).__init__(name)

        self.name = name
        self.address = address
        self.port = port
        self.onData = self.logToFile    # fallback

    def logToFile(self, text):
        """logToFile(text)

        Logs to a file (log.txt).

        :param text:    The data received.
        """
        print(text)
        with open('./log.txt', 'a+') as log:
            json.dump(text, log)
            log.write('\n')

    def listen(self, route, onData):
        """listen(route, onData)

        Listens to messages on *route* and calls *onData*.

        :param route:       The path to listen on. (str)
        :param onData:      The callback function. (func(json))
        """
        self.onData = onData

        self.route(route, methods=['POST'])(self.__handle_post)
        self.run(host=self.address, port=self.port, debug=True)

    def __handle_post(self):
        # TODO: this is a weak check that message is json.
        #       json.dumps/load may blow up. fix it.
        if 'application/json' in request.headers.get('Content-Type'):
            raw = json.dumps(request.json)
            self.onData(json.loads(raw))
            self.logToFile(raw)
            #print()
            return Response('OK', 200)
        return Response('Unsupported Media Type', 415)
