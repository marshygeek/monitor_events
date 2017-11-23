import json
import requests
import websocket
from timeit import default_timer
from time import time


class Chrome:
    def __init__(self, tab=0, timeout=10, host='localhost', port=9222) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.message_counter = 1000

        response = requests.get('http://{}:{}/json'.format(self.host, self.port))
        tabs = json.loads(response.text)
        wsurl = tabs[tab]['webSocketDebuggerUrl']
        self.ws = websocket.create_connection(wsurl)
        self.ws.settimeout(self.timeout)

        #self.call_method('Runtime.enable')
        self.call_method('Page.enable')

    def wait_loop(self, **kwargs):
        event = kwargs.get('event', None)
        message_id = kwargs.get('message_id', None)

        start = default_timer()
        while default_timer() - start < self.timeout:
            try:
                message_json = self.ws.recv()
                message = json.loads(message_json)
            except websocket.WebSocketTimeoutException:
                raise
            except websocket.WebSocketException:
                raise

            if event and 'method' in message and message['method'] == event:
                return
            if message_id and 'id' in message and message['id'] == message_id:
                return message
        raise TimeoutError

    def wait_event(self, event):
        self.wait_loop(event=event)

    def call_method(self, method, **kwargs):
        self.message_counter += 1
        message = {'method': method, 'params': kwargs, 'id': self.message_counter}
        message_json = json.dumps(message)
        self.ws.send(message_json)
        result = self.wait_loop(message_id=message['id'])
        return result['result']

    def close(self):
        self.ws.close()

    def show_events(self, base):
        start = default_timer()
        while default_timer() - start < self.timeout:
            print(time() - base)
            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
            except websocket.WebSocketTimeoutException:
                raise
            except websocket.WebSocketException:
                raise
            print(parsed_message['method'])
        print("END")
        raise TimeoutError

