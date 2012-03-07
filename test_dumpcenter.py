from time import sleep
from datetime import datetime
from dumpcenter import DumpCenter


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


def test_get_wilecard(dump):
    dump.set(foo=123, bar=True)
    assert dump.get('foo', 'bar') == {'foo': 123, 'bar': True}
    assert dump.get('*') == {'foo': 123, 'bar': True}


def test_get_pattern(dump):
    dump.set(meanSpeed=123, meanPower=456, foo=False)
    assert dump.get('mean*') == {'meanSpeed': 123, 'meanPower': 456}


def test_get_complex_pattern(dump):
    dump.set(meanSpeed=1, meanPower=2, rpm1=3, rpm2=4, foo=0)
    message = {'meanSpeed': 1, 'meanPower': 2, 'rpm1': 3, 'rpm2': 4}
    assert dump.get('mean*', 'rpm?') == message


def test_get_pattern_and_name(dump):
    dump.set(meanSpeed=1, meanPower=2, rpm1=3, rpm2=4, foo=0)
    message = {'meanSpeed': 1, 'rpm1': 3, 'rpm2': 4}
    assert dump.get('rpm[12]', 'meanSpeed') == message


def test_gets_latest_value(dump):
    dump.set(a=0, b=1, foo=-1)
    dump.set(a=5, b=6, foo=-2)
    dump.set(a=8, b=9, foo=-3)
    assert dump.get('?') == {'a': 8, 'b': 9}


def test_when_all_values_are_discarded_get_returns_none(dump):
    dump.set(a=0, b=1, foo=-1)
    sleep(1)
    assert dump.get('?') == {'a': None, 'b': None}


# Period


def test_get_period(dump):
    dump.set(a=0, b=1, foo=-1)
    dump.set(a=5, b=6, foo=-2)
    dump.set(a=8, b=9, foo=-3)
    assert dump.get('?', period=1) == {'a': [0, 5, 8], 'b': [1, 6, 9]}


def test_when_all_values_are_discarded_get_period_returns_empty_lists(dump):
    dump.set(a=0, b=1, foo=-1)
    sleep(1)
    assert dump.get('?', period=9) == {'a': [], 'b': []}


def test_old_values_are_discarded_get_period(dump):
    dump.set(a=0, b=1, foo=-1)
    sleep(1)
    dump.set(a=5, b=6, foo=-2)
    dump.set(a=8, b=9, foo=-3)
    assert dump.get('?', period=9) == {'a': [5, 8], 'b': [6, 9]}


def test_get_period_truncates(dump):
    dump.set(a=0, b=1, foo=-1)
    sleep(0.5)
    dump.set(a=5, b=6, foo=-2)
    dump.set(a=8, b=9, foo=-3)
    assert dump.get('?', period=0.5) == {'a': [5, 8], 'b': [6, 9]}


# Timestamps


def test_get_timestamps(dump):
    dump.set(a=2, b=3)
    dump.set(a=8, b=9)
    d = dump.get('?', timestamps=True)  # {'a': [t, 8], 'b': [t, 9]}
    assert len(d['a']) == 2
    assert type(d['a'][0]) == datetime
    assert d['a'][1] == 8
    assert len(d['b']) == 2
    assert type(d['b'][0]) == datetime
    assert d['b'][1] == 9


def test_get_timestamps_with_period(dump):
    dump.set(a=2, b=3)
    dump.set(a=8, b=9)
    # {'a': [[t, 2], [t, 8]], 'b': [[t, 3], [t, 9]]}
    d = dump.get('?', timestamps=True, period=1)
    [[t1, v1], [t2, v2]] = d['a']
    assert type(t1) == type(t2) == datetime
    assert v1 == 2 and v2 == 8
    [[t1, v1], [t2, v2]] = d['b']
    assert type(t1) == type(t2) == datetime
    assert v1 == 3 and v2 == 9
