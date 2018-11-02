"""
Stores data through reboots.
"""

import pickle
import os
import traceback

from .utils import DotDict

class PersistentStorage(object):
    def __init__(self, path):
        self.path = path
        if os.path.isfile(path):
            try:
                with open(path, 'rb') as f:
                    self.storage = pickle.load(f)
            except:
                print(traceback.format_exc())
                self.storage = DotDict()
        else:
            self.storage = DotDict()

    def save(self):
        try:
            with open(self.path, 'wb') as f:
                pickle.dump(self.storage, f)
        except:
            print(traceback.format_exc())
            pass

    def __iter__(self):
        return self.storage.__iter__()

    def __next__(self):
        return self.storage.__next__()

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.store(key, value)

    def __len__(self):
        return len(self.storage)

    def __contains__(self, key):
        return key in self.storage

    def store(self, key, value):
        self.storage[key] = value

    def get(self, key):
        if key in self.storage:
            return self.storage[key]
        else:
            return None

    def clear(self, key=None):
        if key:
            if key in self.storage:
                del self.storage[key]
        else:
            self.storage.clear()

