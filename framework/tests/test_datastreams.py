__author__ = 'christian'

from framework import modmaster, datastreams
import pytest
import time

def test_basic_datastream():
    modmaster.load_mod("framework.tests.resources.basic_datastream.testMod1")
    modmaster.load_mod("framework.tests.resources.basic_datastream.testMod2")
    mod1 = modmaster.get_mod("test1")
    mod2 = modmaster.get_mod("test2")
    assert mod1.streamData == "blank"
    mod1.readStream()
    assert mod1.streamData == "blank"
    mod2.pushStream()
    mod1.readStream()
    assert mod1.streamData == "fart"
    modmaster.kill_all_mods()


def test_datastream_locking():
    modmaster.load_mod("framework.tests.resources.datastream_locking.testMod1")
    modmaster.load_mod("framework.tests.resources.datastream_locking.testMod2")
    modmaster.load_mod("framework.tests.resources.datastream_locking.testMod3")
    mod1 = modmaster.get_mod("test1")
    mod2 = modmaster.get_mod("test2")
    mod3 = modmaster.get_mod("test3")
    mod2.pushStream()
    mod1.readStream()
    assert mod1.streamData is 100
    with pytest.raises(datastreams.LockError):
        mod3.pushStream()
    mod1.readStream()
    assert mod1.streamData is 100
    mod3.lockStream()
    mod3.pushStream()
    mod1.readStream()
    assert mod1.streamData is 50
    mod2.pushStream()
    mod1.readStream()
    assert mod1.streamData is 100
    modmaster.kill_all_mods()
    datastreams.purge_datastreams()


def test_datastream_events():
    modmaster.load_mod("framework.tests.resources.datastream_events.testMod1")
    mod1 = modmaster.get_mod("test1")
    assert len(modmaster.list_modules()) is 1
    mod1.reset()
    assert mod1.updated is False
    assert mod1.incremented is False
    stream = datastreams.get_stream("testStream")
    stream.push(0, "tester", autolock=True)
    time.sleep(.5)
    assert mod1.updated is True
    assert mod1.incremented is False
    mod1.reset()
    assert mod1.updated is False
    assert mod1.incremented is False
    stream.push(1, "tester", autolock=True)
    time.sleep(.5)
    assert mod1.updated is True
    assert mod1.incremented is True
    mod1.reset()
    assert mod1.updated is False
    assert mod1.incremented is False
    modmaster.kill_all_mods()
    datastreams.purge_datastreams()