import aiohttp
from datetime import datetime, timedelta
import logging
import re

from .base import BaseCheck
from .exceptions import *
from src.utils.other import get_user_agent


logger = logging.getLogger(__name__)


class TinkCheck(BaseCheck):
    async def valid(self) -> None:
        if re.match(r'^(https?://)?link\.tbank\.ru/[A-Za-z0-9]{8,16}$', self.url) is None:
            raise InvalidCheckUrl

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
            'origin': 'https://atm-receipt.cdn-tinkoff.ru',
            'priority': 'u=1, i',
            'referer': 'https://atm-receipt.cdn-tinkoff.ru/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': get_user_agent(),
        }
        params = {
            'short_link': self.url.split('/')[-1],
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url='https://www.tinkoff.ru/api/v1/short_link_parameters',
                    params=params,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    json_response = await response.json()
                    result = json_response['payload']['params']

        except Exception as e:
            logger.error(e)
            raise UnknownCheckError

        self.amount = result['operationAmount']

        if not len(result):
            raise CheckNotFound

        opearation_datetime = datetime.strptime(result['operationDateTime'], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - opearation_datetime > timedelta(days=3):
            raise InvalidCheckDate

        if not (result['operationDstNumber'][:6] == self.card[:6] and \
                 result['operationDstNumber'][-4:] == self.card[-4:]):
            raise InvalidCheckCard
