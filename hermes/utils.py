import os
import subprocess

import yaml


def calculate_size(size):
    """
    Given some integer number of bytes, converts it to the largest possible unit till the number
    is somewhere between the range of [1, 1024).

    :param size:
    :return: a human readable string for the size
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    unit = 0
    while size > 1024:
        size /= 1024
        unit += 1
    return str(round(size, 2 if unit < 4 else 4)) + " " + units[unit]


def dict_to_list(d):
    """Converts an ordered dict into a list."""
    # make sure it's a dict, that way dict_to_list can be used as an
    # array_hook.
    d = dict(d)
    try:
        return [str(d[x], 'utf-8') for x in range(len(d))]
    except KeyError:
        raise ValueError('dict is not a sequence')


def run_popen(command):
    if isinstance(command, str):
        command = command.split()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out, err


def get_git_hash():
    """
    This function attempts to get the hash of the head commit, assuming that hermes is being
    run out of a git repo, otherwise this will just return None

    :return: str hash assuming hermes is in git repo, otherwise None
    """
    git_hash = None
    if os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".git")):
        current_dir = os.getcwd()
        git_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", )
        os.chdir(git_dir)
        out, _ = run_popen("git rev-parse HEAD --short")
        os.chdir(current_dir)
        git_hash = str(out, 'utf-8').strip()
    return git_hash


def check_pid(pid):
    """
    This function checks if the given pid by sending it the 0 signal (which does nothing).
    However, when this function is run on windows, it will interpret the signal as
    signal.CTRL_C_EVENT which will kill the process, so we can really only use this on
    Unix.

    :param pid:
    :return: boolean whether the process exists or not
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    else:
        return True


def load_config(config_file):
    """Utility function to load the configuration file for Hermes and convert all dictionaries
    inside the config file to DotDict objects instead"""
    config = yaml.safe_load(open(config_file))
    return convert(config)


def convert(node):
    """Iterate through the node's items (if dict or list) converting them. All dicts are changed
    into DotDict objects"""
    if isinstance(node, dict):
        for key, value in node.items():
            node[key] = convert(value)
        node = DotDict(node)
    elif isinstance(node, list):
        for elem in range(len(node)):
            node[elem] = convert(node[elem])
    return node


class DotDict(dict):
    """Utility class that allows for dot notation on dictionaries"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __contains__ = dict.__contains__
    
    def __getstate__(self):
        return self.__dict__
    def __setstate__(self, d):
        self.__dict__.update(d)


def file_tail(file_name, num):
    """
    Gets the last x number of lines from file_name. Basically the 'tail' unix command,
    but in python.

    :param file_name:
    :param lines:
    :return:
    """
    """
    bufsize = 8192
    fsize = os.stat(file_name).st_size
    iterator = 0
    with open(file_name) as f:
        if bufsize > fsize:
            bufsize = fsize - 1
            data = []
            while True:
                iterator += 1
                f.seek(fsize - bufsize * iterator)
                data.extend(f.readlines())
                if len(data) >= lines or f.tell() == 0:
                    return [x.strip() for x in data[-lines:]]
    return []
    """
    lines = []
    with open(file_name) as f:
        for line in f:
            if len(lines) > num:
                lines.pop(0)
            lines.append(line)
    return lines
