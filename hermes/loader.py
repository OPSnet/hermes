"""
Module for that allows for dynamic loading/reloading of modules for hermes to use such that we
don't have to necessarily build all of our functionality into the core of hermes, but rather
in separate files each with its own purpose that we've then registered to be run given a
certain command (like getting a privmsg) or matches some regex rule.
"""

import importlib.util
import inspect
import os
import re
import sys


def load_modules():
    """
    Loads all the modules from the the modules/ directory within hermes and then checks if
    the ~/hermes/modules folder exists and then loads any modules there as well (if it exists).
    Note, we want all modules to have unique names otherwise any in ~/hermes/modules will overwrite
    any in the modules/ directory.

    :return: a dictionary containing all loaded modules where they key is module name (filename)
             and the value is the loaded module definition
    """
    modules = {}
    modules_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")
    modules.update(_get_all_modules(modules_dir))
    local_dir = os.path.join(os.path.expanduser("~/hermes"), "modules")
    if os.path.isdir(local_dir):
        modules.update(_get_all_modules(local_dir))
    return modules


def _get_all_modules(directory):
    modules = {}
    for path in os.listdir(directory):
        module_path = os.path.join(directory, path)
        if os.path.isfile(module_path) and module_path.endswith(".py"):
            load_module(modules, module_path)
    return modules


def load_module(modules, module_path):
    name = os.path.basename(module_path)[:-3]
    spec = importlib.util.spec_from_file_location(name, module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.__callables__ = parse_module(mod)
    mod.__mod_path__ = module_path
    modules[name] = mod
    sys.modules[name] = mod


def _parse_callable(obj):
    obj.admin_only = getattr(obj, "admin_only", False) is True
    obj.disabled = getattr(obj, 'disabled', False) is True
    if not hasattr(obj, 'events'):
        obj.events = ['pubmsg']
    else:
        if isinstance(obj.events, str):
            obj.events = [obj.events]
        obj.events = [event.lower() for event in obj.events]
    if hasattr(obj, 'commands'):
        if isinstance(obj.commands, str):
            obj.commands = [obj.commands]
        obj.commands = [command.lower() for command in obj.commands]
    if hasattr(obj, 'rules'):
        if isinstance(obj.rules, str):
            obj.rules = [[obj.rules, 0]]
        assert(isinstance(obj.rules, list))
        for i in range(len(obj.rules)):
            obj.rules[i] = re.compile(*obj.rules[i])

    obj.help = getattr(obj, "help", None)
    obj.examples = getattr(obj, "examples", [])
    return obj


def parse_module(mod):
    callables = []
    for name, func in inspect.getmembers(mod, inspect.isfunction):
        if any(hasattr(func, attr) for attr in ('rules', 'commands')):
            callables.append(_parse_callable(func))
    return callables
