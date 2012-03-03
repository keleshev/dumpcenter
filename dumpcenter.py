#! /usr/bin/env python
import socket
import json
#from datetime import datetime


class DumpCenterServer(object):

    def __init__(self, port=1042):
        self.state = {}
        self.server = socket.socket()
        #self.server.bind((socket.gethostname(), port))
        self.server.bind(('', port))
        self.server.listen(0)
        while True:
            client, address = self.server.accept()
            #print '<>', client, address
            #assert False
            message = ''
            while True:
                buf = client.recv(4096)
                message += buf
                if buf.endswith('\n'):
                    break
                if buf == '':
                    assert False
            #print '>', message
            if message.startswith('set '):
                self.set_request(json.loads(message[4:-1]))
            elif message.startswith('get '):
                data = self.get_request(message[4:-1])
                client.send(json.dumps(data).replace('\n', ' ') + '\n')
            elif message.startswith('die'):
                print '> bye, suckers!'
                break
            elif message.startswith('clr'):
                self.state = {}
            #client.shutdown(socket.SHUT_RDWR)
            client.close()
        #self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()

    def set_request(self, data):
        for key, value in data.items():
            self.state[key] = value
            #if key not in self.state:
            #    self.state[key] = []
            #self.state[key].append((datetime.isoformat(), value))

    def get_request(self, pattern):
        keys = pattern.split()
        if keys[0] == pattern:
            return self.state[pattern]
        return dict((k, v) for (k, v) in self.state.items() if k in keys)


class DumpCenter(object):

    def __init__(self, address='localhost:1042'):
        self.host, self.port = address.split(':')
        self.port = int(self.port)

    def _send(self, message):
        client = socket.socket()
        client.connect((self.host, self.port))
        client.send(message.replace('\n', ' ') + '\n')
        #client.shutdown(socket.SHUT_RDWR)
        client.close()

    def set(self, *arg, **kw):
        data = arg[0] if arg else kw
        self._send('set ' + json.dumps(data))

    def get(self, key):
        client = socket.socket()
        client.connect((self.host, self.port))
        client.send('get ' + key + '\n')
        message = ''
        while True:
            message += client.recv(4096)
            if message.endswith('\n'): # or message == '':
                break
        #client.shutdown(socket.SHUT_RDWR)
        client.close()
        return json.loads(message)

    def die(self):
        self._send('die')

    def clr(self):
        self._send('clr')


if __name__ == '__main__':
    DumpCenterServer()
