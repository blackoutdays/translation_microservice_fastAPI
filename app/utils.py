import logging
import asyncio
from typing import Any, Dict
import aiohttp

logger = logging.getLogger(__name__)

YANDEX_API_KEY = 'AQVNzbs__XJFQV3w3Ev077ozVA7xD8m24W-KXFiQ'
YANDEX_TRANSLATE_URL = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
MAX_REQUESTS_PER_SECOND = 20
semaphore = asyncio.Semaphore(MAX_REQUESTS_PER_SECOND)

async def translate_text(text: str, source_language: str, target_language: str) -> str:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {YANDEX_API_KEY}',
    }

    body = {
        "sourceLanguageCode": source_language,
        "targetLanguageCode": target_language,
        "texts": [text],
        "folderId": "b1g12h7imnoq5u2mb3fa"
    }

    async with semaphore:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(YANDEX_TRANSLATE_URL, headers=headers, json=body) as response:
                    if response.status == 200:
                        translated_text = (await response.json())['translations'][0]['text']
                        return translated_text
                    elif response.status == 429:
                        logger.error("Ошибка 429: Лимит запросов превышен. Повтор через 1 секунду.")
                        await asyncio.sleep(1)
                        return text
                    else:
                        logger.error(f"Ошибка перевода: {response.status}. Текст ошибки: {await response.text()}")
                        return text
            except aiohttp.ClientError as e:
                logger.error(f"Ошибка при отправке запроса: {str(e)}")
                return text

async def send_translated_data_to_service(translated_data: Dict[str, Any], service_url: str):
    headers = {'Content-Type': 'application/json'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(service_url, json=translated_data, headers=headers) as response:
                if response.status == 200:
                    logger.info('Данные успешно отправлены в микросервис.')
                    return await response.json()
                else:
                    logger.error(
                        f'Ошибка при отправке данных: {response.status}. Текст ошибки: {await response.text()}')
                    return None
    except Exception as e:
        logger.error(f"Ошибка при отправке данных в микросервис: {str(e)}")
        return None
