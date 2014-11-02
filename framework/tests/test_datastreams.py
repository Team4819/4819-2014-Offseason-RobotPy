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