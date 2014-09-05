__author__ = 'christian'

from framework import modmaster, datastreams
import pytest


def test_basic_datastream():
    modmaster.load_mod("framework.tests.resources.test_basic_datastream.testMod1")
    modmaster.load_mod("framework.tests.resources.test_basic_datastream.testMod2")
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
    modmaster.load_mod("framework.tests.resources.test_datastream_locking.testMod1")
    modmaster.load_mod("framework.tests.resources.test_datastream_locking.testMod2")
    modmaster.load_mod("framework.tests.resources.test_datastream_locking.testMod3")
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

