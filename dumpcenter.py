#! /usr/bin/env python
import socket
import json
from fnmatch import fnmatchcase
from datetime import datetime


#def serialize(obj):
#    def datetime_handler(obj):
#        if hasattr(obj, 'isoformat'):
#            return obj.isoformat()
#        else:
#            raise TypeError
#    message = json.dumps(obj, default=datetime_handler)
#    assert '\n' not in message
#    return message


#def deserialize(message):
#    return json.loads(message)


class DumpProtocol(object):

    def __init__(self, address='localhost:1042', client=None):
        self._address = address
        self._client = client

    def __enter__(self):
        if not self._client:
            self._client = socket.socket()
            host, port = self._address.split(':')
            self._client.connect((host, int(port)))
        return self

    def send(self, message):
        assert '\n' not in json.dumps(message)
        self._client.send(json.dumps(message) + '\n')

    def receive(self):
        message = ''
        while True:
            message += self._client.recv(4096)
            if message.endswith('\n'): # or message == '':
                break
        return json.loads(message)

    def __exit__(self, exception_type, value, traceback):
        #self._client.shutdown(socket.SHUT_RDWR)
        self._client.close()


class DumpCenterServer(object):

    def __init__(self, port=1042, period=0.5):
        self.dump = Dump()
        self.period = period
        self.server = socket.socket()
        #self.server.bind((socket.gethostname(), port))
        self.server.bind(('', port))
        self.server.listen(0)
        while True:
            client, address = self.server.accept()
            with DumpProtocol(client=client) as protocol:
                command, argument = protocol.receive()
                if command == 'get':
                    protocol.send(self.dump.get(*argument[0], **argument[1]))
                elif command == 'set':
                    self.dump.set(argument)
                elif command == 'clr':
                    self.dump.clr()
        #self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()


class DumpCenter(object):

    def __init__(self, address='localhost:1042'):
        self.address = address

    def set(self, *arg, **kw):
        data = arg[0] if arg else kw
        with DumpProtocol(self.address) as protocol:
            protocol.send(['set', data])

    def get(self, *arg, **kw):
        with DumpProtocol(self.address) as protocol:
            protocol.send(['get', [arg, kw]])
            return protocol.receive()

    def clr(self):
        with DumpProtocol(self.address) as protocol:
            protocol.send(['clr', None])


class Dump(object):

    def __init__(self, address='localhost:1042'):
        self._state = {}

    def set(self, *arg, **kw):
        data = arg[0] if arg else kw
        for key, value in data.items():
            #self._state[key] = value
            if key not in self._state:
                self._state[key] = []
            self._state[key].append([datetime.now().isoformat(), value])

    def _get_match(self, argument):
        patterns = [a for a in argument if self._is_pattern(a)]
        keys = [a for a in argument if not self._is_pattern(a)]
        patterns_match = {}
        for p in patterns:
            for k in self._state.keys():
                if fnmatchcase(k, p):
                    patterns_match[k] = self._state.get(k)
        keys_match = dict((key, self._state.get(key)) for key in keys)
        return dict(patterns_match.items() + keys_match.items())

    def get(self, *arg, **kw):
        argument, options = arg, kw
        #self._truncate()
        match = self._get_match(argument)
        if options.get('period'):
            for key in match:
                if match[key]:
                    match[key] = list(zip(*match[key])[1])
                else:
                    match[key] = None
        else:
            for key in match:
                if match[key]:
                    match[key] = match[key][-1][1]
                else:
                    match[key] = None
        if len(argument) == 1 and not self._is_pattern(argument[0]):
            return match.get(argument[0])
        return match

    def _truncate(self):
        now = datetime.now()
        for key in self._state:
            self._state[key] = [[t, v] for [t, v] in self._state[key]
                               if (now - t).seconds > self.period]

    def _is_pattern(self, s):
        return '*' in s or '?' in s or '[' in s or ']' in s

    def clr(self):
        self._state = {}


if __name__ == '__main__':
    DumpCenterServer()
