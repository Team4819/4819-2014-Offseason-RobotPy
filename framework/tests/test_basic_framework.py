__author__ = 'christian'

from framework import modmaster
import shutil
import os
import time
import pytest


def test_basic_module_load_unload():
    assert len(modmaster.list_modules()) is 0
    modmaster.load_mod("framework.modbase")
    assert len(modmaster.list_modules()) is 1
    module = modmaster.get_mod("generic")
    assert module.name is "generic"
    modmaster.unload_mod("generic")
    assert len(modmaster.list_modules()) is 0


def test_module_reload():
    shutil.copyfile("framework/tests/resources/test_module_reload/testMod1.py", "framework/tests/resources/test_module_reload/test.py")
    assert len(modmaster.list_modules()) is 0
    modmaster.load_mod("framework.tests.resources.test_module_reload.test")
    assert len(modmaster.list_modules()) is 1
    module = modmaster.get_mod("test")
    assert module.getMessage() == "Get out of here!"
    shutil.copyfile("framework/tests/resources/test_module_reload/testMod2.py", "framework/tests/resources/test_module_reload/test.py")
    time.sleep(1)
    module.reload()
    assert module.getMessage() == "hello there most excellent tester!"
    modmaster.unload_mod("test")
    os.remove("framework/tests/resources/test_module_reload/test.py")


def test_config_loading():
    assert len(modmaster.list_modules()) is 0
    modmaster.load_startup_mods("framework/tests/resources/test_config_loading/mods.conf")
    assert len(modmaster.list_modules()) is 1
    module = modmaster.get_mod("test1")
    assert module.getMessage() == "Get out of here!"
    modmaster.load_mod("test2")
    assert len(modmaster.list_modules()) is 2
    module = modmaster.get_mod("test2")
    assert module.getMessage() == "Get out of here, Now!"
    modmaster.kill_all_mods()
    assert len(modmaster.list_modules()) is 0


def test_exception_handling():
    assert len(modmaster.list_modules()) is 0
    modmaster.load_startup_mods("framework/tests/resources/test_exception_handling/mods.conf")
    assert len(modmaster.list_modules()) is 1
    mod = modmaster.get_mod("exceptional")
    mod.async("setMessage")
    time.sleep(1)
    assert mod.message == "hi"
    mod.async("setMessage")
    time.sleep(1)
    assert mod.message == "Problem solved!"
    modmaster.kill_all_mods()
    assert len(modmaster.list_modules()) is 0