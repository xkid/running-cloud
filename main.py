#!python3
from flask import Flask
from flask_sockets import Sockets
import logging
import asyncio
import os
from hbmqtt.broker import Broker
import yaml
import threading


app = Flask(__name__)
sockets = Sockets(app)


@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)


@app.route('/')
def hello():
    return '<h1>Hello WebSocket!</h1>'

@asyncio.coroutine
def broker_coro():
    stream = """ 
listeners:
    default:
        max-connections: 443
        type: tcp
    my-ws-1:
        bind: 0.0.0.0:"""+os.environ['PORT']+"""
        type: ws
timeout-disconnect-delay: 2
    """
    config = yaml.load(stream)
    print(config)
    broker = Broker(config=config)
    yield from broker.start()
    
def start_flask():
    app.run(host="0.0.0.0",port=443)

def main_entry:
    #from gevent import pywsgi
    #from geventwebsocket.handler import WebSocketHandler
    #print(os.environ['PORT'])
    #server = pywsgi.WSGIServer(('', int(os.environ['PORT'])), app, handler_class=WebSocketHandler)
    #server.serve_forever()
    t = threading.Thread(target=start_flask)
    t.start()
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)
    asyncio.get_event_loop().run_until_complete(broker_coro())
    asyncio.get_event_loop().run_forever()