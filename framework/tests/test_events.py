__author__ = 'christian'

from framework import events, module_engine
import time


def test_basic_events():
    module_engine.load_module("framework.tests.resources.basic_events.testMod1")
    module_engine.load_module("framework.tests.resources.basic_events.testMod2")
    mod1 = module_engine.get_modules("test1")
    mod2 = module_engine.get_modules("test2")
    assert mod1.index is 1
    mod1.set_callback()
    assert mod1.index is 1
    mod2.fireEvent()
    time.sleep(.1)
    assert mod1.index is 2
    events.trigger_event("test", "tester")
    time.sleep(.1)
    assert mod1.index is 3
    module_engine.kill_all_modules()
    events.remove_callbacks()


def test_state_events():
    module_engine.load_module("framework.tests.resources.state_events.testMod1")
    mod1 = module_engine.get_modules("test1")
    assert mod1.index is 1
    events.trigger_event("test", "tester")
    time.sleep(.1)
    assert mod1.index is 2
    mod1.reset()
    assert mod1.index is 1
    events.start_event("test", "Tester")
    time.sleep(.1)
    assert mod1.index is 2
    mod1.reset()
    assert mod1.index is 1
    events.repeat_callbacks("test1")
    time.sleep(.1)
    assert mod1.index is 2
    events.stop_event("test", "Tester")
    time.sleep(.1)
    mod1.reset()
    assert mod1.index is 1
    events.repeat_callbacks("test")
    time.sleep(.1)
    assert mod1.index is 1
    module_engine.kill_all_modules()
    events.remove_callbacks()