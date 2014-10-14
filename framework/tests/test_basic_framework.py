__author__ = 'christian'

from framework import module_engine
import shutil
import os
import time


def test_basic_module_load_unload():
    assert len(module_engine.list_modules()) is 0
    module_engine.load_module("framework.tests.resources.genericmod")
    assert len(module_engine.list_modules()) is 1
    module = module_engine.get_modules("generic")
    assert module.subsystem is "generic"
    module_engine.unload_module("generic")
    assert len(module_engine.list_modules()) is 0


def test_module_reload():
    shutil.copyfile("framework/tests/resources/module_reload/testMod1.py", "framework/tests/resources/module_reload/test.py")
    assert len(module_engine.list_modules()) is 0
    module_engine.load_module("framework.tests.resources.module_reload.test")
    assert len(module_engine.list_modules()) is 1
    module = module_engine.get_modules("test")
    assert module.getMessage() == "Get out of here!"
    shutil.copyfile("framework/tests/resources/module_reload/testMod2.py", "framework/tests/resources/module_reload/test.py")
    time.sleep(1)
    module.load()
    assert module.getMessage() == "hello there most excellent tester!"
    module_engine.unload_module("test")
    os.remove("framework/tests/resources/module_reload/test.py")


def test_config_loading():
    assert len(module_engine.list_modules()) is 0
    module_engine.load_startup_mods("framework/tests/resources/config_loading/mods.conf")
    assert len(module_engine.list_modules()) is 1
    module = module_engine.get_modules("test1")
    assert module.getMessage() == "Get out of here!"
    module_engine.load_module("test2")
    assert len(module_engine.list_modules()) is 2
    module = module_engine.get_modules("test2")
    assert module.getMessage() == "Get out of here, Now!"
    module_engine.kill_all_modules()
    assert len(module_engine.list_modules()) is 0


def test_exception_handling():
    assert len(module_engine.list_modules()) is 0
    module_engine.load_startup_mods("framework/tests/resources/exception_handling/mods.conf")
    assert len(module_engine.list_modules()) is 1
    mod = module_engine.get_modules("exceptional")
    mod.call_wrap(mod.setMessage)
    assert mod.message == "hi"
    mod.call_wrap(mod.setMessage)
    assert mod.message == "Problem solved!"
    module_engine.kill_all_modules()
    assert len(module_engine.list_modules()) is 0


