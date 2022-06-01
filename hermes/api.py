"""
API interface to Gazelle, operates through the api.php endpoint
"""
import logging
from httpx import AsyncClient, codes
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
        self.client = AsyncClient()

    async def _get(self, parameters):
        try:
            r = await self.client.get(self.api_url, params=parameters)
            if r.status_code == codes.OK:
                response = r.json()
                if response['status'] == 200:
                    return convert(response['response'])
            else:
                LOGGER.error(f'Gazelle API returned status code {r.status_code}')
        except Exception as e:
            LOGGER.warning('Gazelle API network error')
            LOGGER.exception(e)
        return None

    async def get_user(self, user):
        if isinstance(user, int):
            return await self._get({
                "action": "user",
                "user_id": user
            })
        else:
            return await self._get({
                "action": "user",
                "username": user
            })

    async def get_topic(self, topic_id):
        return await self._get({
            "action": "forum",
            "topic_id": topic_id
        })

    async def get_wiki(self, wiki_id):
        return await self._get({
            "action": "wiki",
            "wiki_id": wiki_id
        })

    async def get_request(self, request_id):
        return await self._get({
            "action": "request",
            "request_id": request_id
        })

    async def get_torrent(self, torrent_id):
        return await self._get({
            "action": "torrent",
            "req": "torrent",
            "torrent_id": torrent_id
        })

    async def get_torrent_group(self, group_id):
        return await self._get({
            "action": "torrent",
            "req": "group",
            "group_id": group_id
        })

    async def get_artist(self, artist_id):
        return await self._get({
            "action": "artist",
            "artist_id": artist_id
        })

    async def get_collage(self, collage_id):
        return await self._get({
            "action": "collage",
            "collage_id": collage_id
        })
