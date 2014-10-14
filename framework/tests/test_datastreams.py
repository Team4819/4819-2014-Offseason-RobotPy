__author__ = 'christian'

from framework import module_engine, datastreams
import pytest
import time

def test_basic_datastream():
    module_engine.load_module("framework.tests.resources.basic_datastream.testMod1")
    module_engine.load_module("framework.tests.resources.basic_datastream.testMod2")
    mod1 = module_engine.get_modules("test1")
    mod2 = module_engine.get_modules("test2")
    assert mod1.streamData == "blank"
    mod1.readStream()
    assert mod1.streamData == "blank"
    mod2.pushStream()
    mod1.readStream()
    assert mod1.streamData == "fart"
    module_engine.kill_all_modules()


def test_datastream_locking():
    module_engine.load_module("framework.tests.resources.datastream_locking.testMod1")
    module_engine.load_module("framework.tests.resources.datastream_locking.testMod2")
    module_engine.load_module("framework.tests.resources.datastream_locking.testMod3")
    mod1 = module_engine.get_modules("test1")
    mod2 = module_engine.get_modules("test2")
    mod3 = module_engine.get_modules("test3")
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
    module_engine.kill_all_modules()
    datastreams.purge_datastreams()


def test_datastream_events():
    module_engine.load_module("framework.tests.resources.datastream_events.testMod1")
    mod1 = module_engine.get_modules("test1")
    assert len(module_engine.list_modules()) is 1
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
    module_engine.kill_all_modules()
    datastreams.purge_datastreams()