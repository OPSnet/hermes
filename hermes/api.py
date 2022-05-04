"""
API interface to Gazelle, operates through the api.php endpoint
"""
import logging
import requests
from urllib.parse import urljoin

from .utils import convert

LOGGER = logging.getLogger('hermes')


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

    def _get(self, parameters):
        try:
            r = requests.get(self.api_url, parameters)
            if r.status_code == requests.codes.ok:
                response = r.json()
                if response['status'] == 200:
                    return convert(response['response'])
            else:
                LOGGER.error(f'Gazelle API returned status code {r.status_code}')
        except Exception as e:
            LOGGER.warning('Gazelle API network error')
            LOGGER.exception(e)
        return None

    def get_user(self, user):
        if isinstance(user, int):
            return self._get({
                "action": "user",
                "user_id": user
            })
        else:
            return self._get({
                "action": "user",
                "username": user
            })

    def get_topic(self, topic_id):
        return self._get({
            "action": "forum",
            "topic_id": topic_id
        })

    def get_wiki(self, wiki_id):
        return self._get({
            "action": "wiki",
            "wiki_id": wiki_id
        })

    def get_request(self, request_id):
        return self._get({
            "action": "request",
            "request_id": request_id
        })

    def get_torrent(self, torrent_id):
        return self._get({
            "action": "torrent",
            "req": "torrent",
            "torrent_id": torrent_id
        })

    def get_torrent_group(self, group_id):
        return self._get({
            "action": "torrent",
            "req": "group",
            "group_id": group_id
        })

    def get_artist(self, artist_id):
        return self._get({
            "action": "artist",
            "artist_id": artist_id
        })

    def get_collage(self, collage_id):
        return self._get({
            "action": "collage",
            "collage_id": collage_id
        })
