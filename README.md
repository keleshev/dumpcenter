DumpCenter
==========

Centralized distributed process-cummunication client-server system
------------------------------------------------------------------

To pass messages between two processes (possibly distributed over 
a network), launch the server:

    $ ./dumpcenter

Send a message:

    # Process A
    from dumpcenter import DumpCenter
    dump = DumpCenter()
    dump.set(message_from_a='Hello, process B.')

Receive a message:

    # Process B
    assert dump.get('message_from_a') == 'Hello, process B.'

Receive previous messages over a period (in seconds):

    # Process A
    dump.set(message_from_a='Hello, again, B.")

    # Process B
    messages = dump.get('message_from_a', period=30) 
    assert messages == ['Hello, process B.', 'Hello, again, B.']

Receive previous messages with their timestamps:

    # Process B
    messages = dump.get('message_from_a', period=30, timestamps=True)
    assert messages == [[datetime(2012, 3, 8, 23, 56, 59, 483822),
                         'Hello, process B.'],
                        [datetime(2012, 3, 8, 23, 56, 01, 948389), 
                         'Hello, again, B.']]

Receive all available messages:

    # Process C
    dump.set(message_from_c='Hello from C.')

    # Process B
    assert dump.get('*') == {'message_from_c': 'Hello from C.',
                             'message_from_a': 'Hello, again, B.'}

Receive messages matching pattern (`*`, `?`, and `[]`):

    # Process B
    assert dump.get('*_from[ca]') == {'message_from_c': 'Hello from C.',
                                      'message_from_a': 'Hello, again, B.'} 

Send compound messages (including datatypes which can be JSON-serialized):

    # Process A
    dump.set(message_from_a={'hello': ['list', True, None, 123.56, {}]})

For more examples see `test_dumpcenter.py`.
