__author__ = 'christian'

from framework import modmaster
import shutil
import os

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
    module.reload()
    assert module.getMessage() == "hello there most excellent tester!"
    modmaster.unload_mod("test")
    os.remove("framework/tests/resources/test_module_reload/test.py")