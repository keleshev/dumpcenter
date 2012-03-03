#from threading import Thread
#from multiprocessing import Process
#from time import sleep

from dumpcenter import DumpCenter#, DumpCenterServer

#thread = None

#def _setup_module(m):
#    m.thread = Thread(target=DumpCenterServer)
#    m.thread.daemon = True
#    m.thread.start()
#
#def _teardown_module(m):
#    DumpCenter().die()
#    m.thread.join()


def pytest_funcarg__dump(request):
    dump = DumpCenter()
    dump.clr()
    return dump


def test_get_one_value(dump):
    dump.set(foo=123)
    assert dump.get('foo') == 123


def test_get_compound_value(dump):
    dump.set(foo={'foo': True, 'bar': None})
    assert dump.get('foo') == {'foo': True, 'bar': None}


def test_set_dict(dump):
    dump.set({'foo': 123})
    assert dump.get('foo') == 123


def test_get_two_values(dump):
    dump.set(foo=123, bar=True)
    assert dump.get('foo bar') == {'foo': 123, 'bar': True}


def test_clr(dump):
    dump.set(foo=123, bar=True)
    assert dump.get('foo bar') == {'foo': 123, 'bar': True}
    dump.clr()
    assert dump.get('foo bar') == {'foo': None, 'bar': None}  # HACK

#def test_wilecard():
#def test_pattern():
#def test_parrern_and_names():

#def test_timestamps():
#def test_period():
#def test_period_with_timestamps():
#def test_mean()"


