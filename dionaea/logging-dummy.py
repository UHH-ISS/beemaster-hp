#!/usr/bin/python

from flask import Flask, request, json, Response

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handlePost():
    if 'application/json' in request.headers.get('Content-Type'):
        raw = json.dumps(request.json)
        print(raw)
        with open('./log.txt', 'a+') as log:
            log.write(raw + '\n\n')
    return Response('OK', 200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
