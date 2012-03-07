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
        def encode_datetime(obj):
            if isinstance(obj, datetime):
                return {'__datetime__': str(obj)}
            raise TypeError(repr(obj) + " is not JSON serializable")
        #assert '\n' not in json.dumps(message)
        self._client.send(json.dumps(message, default=encode_datetime) + '\n')

    def receive(self):
        def decode_datetime(obj):
            if '__datetime__' in obj:
                return datetime.strptime(obj['__datetime__'],
                                         '%Y-%m-%d %H:%M:%S.%f')
            return obj
        message = ''
        while True:
            message += self._client.recv(4096)
            if message.endswith('\n'): # or message == '':
                break
        return json.loads(message, object_hook=decode_datetime)

    def __exit__(self, exception_type, value, traceback):
        #self._client.shutdown(socket.SHUT_RDWR)
        self._client.close()


class DumpCenterServer(object):

    def __init__(self, port=1042, lifetime=1):
        self.dump = Dump(lifetime)
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

    def __init__(self, lifetime=1):
        self._lifetime = lifetime
        self._state = {}

    def set(self, *arg, **kw):
        data = arg[0] if arg else kw
        for key, value in data.items():
            if key not in self._state:
                self._state[key] = []
            self._state[key].append([datetime.now(), value])

    def get(self, *arg, **kw):
        arguments, options = arg, kw
        self._state = self._truncate(self._state, self._lifetime)
        match = self._get_match(arguments)
        if options.get('period'):
            match = self._truncate(match, options['period'])

        if options.get('period') and options.get('timestamps'):
            transform = lambda x: x if x else []
        elif options.get('period'):
            transform = lambda x: list(zip(*x)[1]) if x else []
        elif options.get('timestamps'):
            transform = lambda x: x[-1] if x else []
        else:
            transform = lambda x: x[-1][1] if x else None

        match = dict((key, transform(val)) for key, val in match.items())

        if len(arguments) == 1 and not self._is_pattern(arguments[0]):
            return match.get(arguments[0])
        return match

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

    def _truncate(self, state, period):
        now = datetime.now()
        for key in state:
            state[key] = [[t, v] for [t, v] in state[key]
                          if (now - t).total_seconds() < period]
        return state

    def _is_pattern(self, s):
        return '*' in s or '?' in s or '[' in s or ']' in s

    def clr(self):
        self._state = {}


if __name__ == '__main__':
    DumpCenterServer()
