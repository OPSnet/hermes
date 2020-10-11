"""
API (not ajax.php) interface for Gazelle to get information from the database
without having to directly connect to it. This class and Database should be
interchangeable in the bot and have it function just fine.
"""
import requests
import json
from urllib.parse import urljoin

from .utils import convert


class GazelleAPI(object):
    def __init__(self, site_url, api_id, api_key, cache):
        self.site_url = site_url
        self.api_id = api_id
        self.api_key = api_key
        self.api_url = urljoin(
            self.site_url,
            'api.php?aid={}&token={}'.format(api_id, api_key)
        )
        self.cache = cache

    def get_user(self, user):
        try:
            if isinstance(user, int):
                r = requests.get(self.api_url, {
                    "action": "user",
                    "user_id": user
                })
            else:
                r = requests.get(self.api_url, {
                    "action": "user",
                    "username": user
                })

            if r.status_code == requests.codes.ok:
                response = r.json()
                return convert(response['response']) if response['status'] == 200 else None
            else:
                return None
        except OSError:
            return None
        except json.decoder.JSONDecodeError:
            return None

    def get_topic(self, topic_id):
        try:
            r = requests.get(self.api_url, {
                "action": "forum",
                "topic_id": topic_id
            })
            if r.status_code == requests.codes.ok:
                response = r.json()
                return convert(response['response']) if response['status'] == 200 else None
            else:
                return None
        except OSError:
            return None

    def get_wiki(self, wiki_id):
        try:
            r = requests.get(self.api_url, {
                "action": "wiki",
                "wiki_id": wiki_id
            })
            if r.status_code == requests.codes.ok:
                response = r.json()
                return convert(response['response']) if response['status'] == 200 else None
            else:
                return None
        except OSError:
            return None

    def get_request(self, request_id):
        try:
            r = requests.get(self.api_url, {
                "action": "request",
                "request_id": request_id
            })
            if r.status_code == requests.codes.ok:
                response = r.json()
                return convert(response['response']) if response['status'] == 200 else None
            else:
                return None
        except OSError:
            return None

    def get_torrent(self, torrent_id):
        try:
            r = requests.get(self.api_url, {
                "action": "torrent",
                "req": "torrent",
                "torrent_id": torrent_id
            })
            if r.status_code == requests.codes.ok:
                response = r.json()
                return convert(response['response']) if response['status'] == 200 else None
            else:
                return None
        except OSError:
            return None

    def get_torrent_group(self, group_id):
        try:
            r = requests.get(self.api_url, {
                "action": "torrent",
                "req": "group",
                "group_id": group_id
            })
            if r.status_code == requests.codes.ok:
                response = r.json()
                return convert(response['response']) if response['status'] == 200 else None
            else:
                return None
        except OSError:
            return None

    def get_artist(self, artist_id):
        try:
            r = requests.get(self.api_url, {
                "action": "artist",
                "artist_id": artist_id
            })
            if r.status_code == requests.codes.ok:
                response = r.json()
                return convert(response['response']) if response['status'] == 200 else None
            else:
                return None
        except OSError:
            return None

    def get_collage(self, collage_id):
        try:
            r = requests.get(self.api_url, {
                "action": "collage",
                "collage_id": collage_id
            })
            if r.status_code == requests.codes.ok:
                response = r.json()
                return convert(response['response']) if response['status'] == 200 else None
            else:
                return None
        except OSError:
            return None

    def disconnect(self):
        pass
