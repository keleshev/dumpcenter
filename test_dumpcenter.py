#from threading import Thread
#from multiprocessing import Process
#from time import sleep
from time import sleep
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
    assert dump.get('foo', 'bar') == {'foo': 123, 'bar': True}


def test_clr_one_value(dump):
    dump.set(foo=123)
    assert dump.get('foo') == 123
    dump.clr()
    assert dump.get('foo') == None


def test_clr_two_values(dump):
    dump.set(foo=123, bar=True)
    assert dump.get('foo', 'bar') == {'foo': 123, 'bar': True}
    dump.clr()
    assert dump.get('foo', 'bar') == {'foo': None, 'bar': None}


def test_wilecard(dump):
    dump.set(foo=123, bar=True)
    assert dump.get('foo', 'bar') == {'foo': 123, 'bar': True}
    assert dump.get('*') == {'foo': 123, 'bar': True}


def test_pattern(dump):
    dump.set(meanSpeed=123, meanPower=456, foo=False)
    assert dump.get('mean*') == {'meanSpeed': 123, 'meanPower': 456}


def test_pattern_complex(dump):
    dump.set(meanSpeed=1, meanPower=2, rpm1=3, rpm2=4, foo=0)
    message = {'meanSpeed': 1, 'meanPower': 2, 'rpm1': 3, 'rpm2': 4}
    assert dump.get('mean*', 'rpm?') == message


def test_pattern_and_name(dump):
    dump.set(meanSpeed=1, meanPower=2, rpm1=3, rpm2=4, foo=0)
    message = {'meanSpeed': 1, 'rpm1': 3, 'rpm2': 4}
    assert dump.get('rpm[12]', 'meanSpeed') == message


def test_gets_latest_value(dump):
    dump.set(a=0, b=1, foo=-1)
    dump.set(a=5, b=6, foo=-2)
    dump.set(a=8, b=9, foo=-3)
    assert dump.get('?') == {'a': 8, 'b': 9}


def test_period(dump):
    dump.set(a=0, b=1, foo=-1)
    dump.set(a=5, b=6, foo=-2)
    dump.set(a=8, b=9, foo=-3)
    assert dump.get('?', period=1) == {'a': [0, 5, 8], 'b': [1, 6, 9]}


def test_old_values_are_discarded(dump):
    dump.set(a=0, b=1, foo=-1)
    sleep(0.5)
    dump.set(a=5, b=6, foo=-2)
    dump.set(a=8, b=9, foo=-3)
    assert dump.get('?', period=1) == {'a': [5, 8], 'b': [6, 9]}


#def test_timestamps():
#def test_period_with_timestamps():
#def test_mean()"


