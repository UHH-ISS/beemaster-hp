from flask import Flask, request, json, Response

class Receiver(Flask):

    def __init__(self, name, address, port):
        super(Receiver, self).__init__(name)
        
        self.name = name
        self.address = address
        self.port = port
        self.onData = self.logToFile # fallback

    def logToFile(self, text):
        '''Log to a file'''
        print(text)
        with open('./log.txt', 'a+') as log:
            log.write(text + '\n\n')

    
    def listen(self, route, onData):
        '''Listen on the given route, call onData when data is received'''
        self.onData = onData

        self.route(route, methods=['POST'])(self.__handle_post)
        self.run(host=self.address, port=self.port, debug=True)


    def __handle_post(self):
        if 'application/json' in request.headers.get('Content-Type'):
            raw = json.dumps(request.json)
            self.onData(raw)
            return Response('OK', 200)
        return Response('Unsupported Media Type', 415)
