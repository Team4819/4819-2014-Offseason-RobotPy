__author__ = 'christian'

from framework import events, modmaster
import time


def test_basic_events():
    modmaster.load_mod("framework.tests.resources.test_basic_events.testMod1")
    modmaster.load_mod("framework.tests.resources.test_basic_events.testMod2")
    mod1 = modmaster.get_mod("test1")
    mod2 = modmaster.get_mod("test2")
    assert mod1.index is 1
    mod1.set_callback()
    assert mod1.index is 1
    mod2.fireEvent()
    time.sleep(.1)
    assert mod1.index is 2
    events.trigger("test", "Tester")
    time.sleep(.1)
    assert mod1.index is 3
    modmaster.kill_all_mods()


def test_state_events():
    modmaster.load_mod("framework.tests.resources.test_state_events.testMod1")
    mod1 = modmaster.get_mod("test1")
    assert mod1.index is 1
    events.trigger("test", "Tester")
    time.sleep(.1)
    assert mod1.index is 2
    mod1.reset()
    assert mod1.index is 1
    events.set_event("test", "Tester", True)
    time.sleep(.1)
    assert mod1.index is 2
    mod1.reset()
    assert mod1.index is 1
    events.refresh_events("test1")
    time.sleep(.1)
    assert mod1.index is 2
    events.set_event("test", "Tester", False)
    time.sleep(.1)
    mod1.reset()
    assert mod1.index is 1
    events.refresh_events("test")
    time.sleep(.1)
    assert mod1.index is 1
    modmaster.kill_all_mods()
    events.purge_events()