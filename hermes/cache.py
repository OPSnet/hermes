"""
Ephemeral storage of arbitrary data.
"""

from datetime import datetime, timedelta

from .utils import DotDict


class CacheObject(object):
    def __init__(self, value, expiry):
        self.value = value
        self.expiry = expiry


class Cache(object):
    def __init__(self, storage=None, expiry=None):
        if storage is not None:
            self.storage = storage
        else:
            self.storage = DotDict()

        if expiry is not None:
            self.expiry = expiry
        else:
            self.expiry = timedelta(7)

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

    def keys(self):
        return self.storage.keys()

    def items(self):
        return self.storage.items()

    def values(self):
        return self.storage.values()

    def store(self, key, value, expiry=None):
        if not expiry:
            expiry = self.expiry
        self.storage[key] = CacheObject(value, datetime.now() + expiry)

    def get(self, key):
        if key in self.storage:
            if self.storage[key].expiry > datetime.now():
                return self.storage[key].value
            else:
                del self.storage[key]

        return None

    def clear(self, key=None):
        if key:
            if key in self.storage:
                del self.storage[key]
        else:
            self.storage.clear()

    def expire(self):
        keys = [k for k in iter(self.storage)]
        for key in keys:
            if self.storage[key].expiry < datetime.now():
                del self.storage[key]
