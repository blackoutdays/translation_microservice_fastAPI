from typing import Any
import logging
import asyncio
from langdetect import detect
from app.utils import translate_text
import random

logger = logging.getLogger(__name__)


async def dynamic_translate(text: str):
    try:
        if not isinstance(text, str) or not text.strip():
            return {"translated_ru": text, "translated_kk": text}

        logger.info(f"Перевод текста: {text}")

        detected_language = detect(text)
        logger.info(f"Определен язык: {detected_language}")

        if detected_language == 'en':
            translated_ru = await translate_text(text, 'en', 'ru') or text
            translated_kk = await translate_text(text, 'en', 'kk') or text
        elif detected_language in ['zh', 'zh-cn']:
            translated_ru = await translate_text(text, 'zh', 'ru') or text
            translated_kk = await translate_text(text, 'zh', 'kk') or text
        elif detected_language == 'ru':
            translated_ru = text
            translated_kk = await translate_text(text, 'ru', 'kk') or text
        else:
            logger.warning(f"Неподдерживаемый язык: {detected_language}. Текст оставлен без перевода.")
            return {'translated_ru': text, 'translated_kk': text}

        return {
            'translated_ru': translated_ru,
            'translated_kk': translated_kk
        }

    except Exception as e:
        logger.error(f"Ошибка в процессе перевода: {str(e)}")
        return {'translated_ru': text, 'translated_kk': text}


async def dynamic_translate_recursive(data: Any) -> Any:
    if isinstance(data, str):
        translations = await dynamic_translate(data)
        return {
            'ru': translations.get('translated_ru', data),
            'kk': translations.get('translated_kk', data)
        }
    elif isinstance(data, dict):
        return {key: await dynamic_translate_recursive(value) for key, value in data.items()}
    elif isinstance(data, list):
        return await asyncio.gather(*[dynamic_translate_recursive(item) for item in data])
    else:
        return data


async def translate_text_with_backoff(text: str, source_language: str, target_language: str, retries: int = 5) -> str:
    for attempt in range(retries):
        try:
            return await translate_text(text, source_language, target_language)
        except Exception as e:
            if '429' in str(e):
                backoff_time = (2 ** attempt) + (random.randint(0, 1000) / 1000)
                logger.warning(f"Лимит запросов превышен. Повтор через {backoff_time} секунд.")
                await asyncio.sleep(backoff_time)
            else:
                logger.error(f"Ошибка перевода текста: {str(e)}")
                return text
    return text


async def translate_english_text(text: str) -> dict:
    try:
        if not isinstance(text, str) or not text.strip():
            return {"translated_ru": text, "translated_kk": text}

        translated_ru = await translate_text_with_backoff(text, 'en', 'ru')
        translated_kk = await translate_text_with_backoff(text, 'en', 'kk')

        return {
            'translated_ru': translated_ru,
            'translated_kk': translated_kk
        }
    except Exception as e:
        logger.error(f"Ошибка перевода текста: {str(e)}")
        return {"translated_ru": text, "translated_kk": text}


async def dynamic_translate_english_recursive(data: Any) -> Any:
    if isinstance(data, str):
        translations = await translate_english_text(data)
        return {
            'ru': translations.get('translated_ru', data),
            'kk': translations.get('translated_kk', data)
        }
    elif isinstance(data, dict):
        return {key: await dynamic_translate_english_recursive(value) for key, value in data.items()}
    elif isinstance(data, list):
        return await asyncio.gather(*[dynamic_translate_english_recursive(item) for item in data])
    else:
        return data