from asyncio import sleep
import logging

# Настройка логирования для приложения
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)  # Создаём логер с именем текущего модуля
import aiohttp
import json


async def ArequestGet(url: str, headers: dict = {}):
    """
    Отправляет асинхронный GET-запрос к указанному URL.

    Args:
        url (str): URL-адрес, на который отправляется запрос.

    Returns:
        aiohttp.ClientResponse: Ответ на запрос.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = headers) as response:
            if response.content_type == 'application/json':
                    response._json_data = await response.json()
            elif response.content_type == 'application/pdf':
                    return await response.read()
            else:
                # Обрабатываем случай, когда Content-Type не соответствует ожидаемому
                response._json_data = await response.text()
            return response


async def ArequestGetJson(url: str, headers: dict = {}):
    """
    Отправляет асинхронный GET-запрос к указанному URL и возвращает ответ в формате JSON, 
    если код статуса равен 200.

    Args:
        url (str): URL-адрес, на который отправляется запрос.

    Returns:
        dict or None: Данные в формате JSON, если код статуса равен 200, иначе None.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f'Ошибка ArequestGetJson, код - {response.status}')
                return None


async def ArequestPost(url: str, json: dict = None, data: aiohttp.FormData = None, headers: dict = None):
    """
    Отправляет асинхронный POST-запрос с JSON-данными или файлами к указанному URL.

    Args:
        url (str): URL-адрес, на который отправляется запрос.
        json (dict, optional): JSON-данные для отправки (если используются).
        data (aiohttp.FormData, optional): Данные для отправки как часть формы (если используются).
        headers (dict, optional): Заголовки для запроса.

    Returns:
        dict: Декодированные JSON-данные из ответа или текст ответа в случае ошибки.
    """
    logger.info(f"json {json}")

    async with aiohttp.ClientSession() as session:
        # Отправка запроса с разными типами данных
        async with session.post(url, json=json, data=data, headers=headers) as response:
            try:
                # Проверяем Content-Type перед парсингом ответа
                if response.content_type == 'application/json':
                    response_data = await response.json()
                elif response.content_type == 'application/pdf':
                    response_data = await response.read()  # Чтение данных как PDF
                elif response.content_type == 'application/octet-stream':
                    # Обработка двоичных данных (например, PDF или другие файлы)
                    response_data = await response.read()  # Читаем как бинарные данные
                else:
                    response_data = await response.text()  # Обработка текста
                    print(f"Unexpected content type: {response.content_type}. Response: {response_data}")
                return response_data
            except aiohttp.ContentTypeError as e:
                # Обрабатываем исключение, если декодирование не удалось
                response_text = await response.text()
                print(f"Failed to decode response: {e}. Response: {response_text}")
                return response_text
            
async def ArequestPut(url: str, json: dict = None, headers: dict = {} ):
    """
    Отправляет асинхронный POST-запрос с JSON-данными к указанному URL.

    Args:
        url (str): URL-адрес, на который отправляется запрос.
        data (dict): Данные, которые будут отправлены в теле запроса.

    Returns:
        aiohttp.ClientResponse: Ответ на запрос.
    """
    # Преобразование данных в строку JSON и обратно в объект для тестирования
    # json = json.dumps(json)
    # json = json.loads(json)
    print(f'Json - {json}, type - {type(json)}')
    
    async with aiohttp.ClientSession() as session:
        async with session.put(url, json=json, headers = headers) as response:
            try:
                # Проверяем Content-Type перед парсингом JSON
                if response.content_type == 'application/json':
                    response._json_data = await response.json()
                elif response.content_type == 'application/pdf':
                    response._json_data = await response.read()
                else:
                    # Обрабатываем случай, когда Content-Type не соответствует ожидаемому
                    response._json_data = await response.text()
                    print(f"Unexpected content type: {response.content_type}. Response: {response}")
                return response
            except aiohttp.ContentTypeError as e:
                # Обрабатываем исключение, если декодирование JSON не удалось
                response_text = await response.text()
                print(f"Failed to decode JSON: {e}. Response: {response_text}")
                return response_text

async def ArequestPostGPT(url: str, payload: str = "", headers: dict = {}):
    """
    Отправляет асинхронный POST-запрос.

    Args:
        url (str): URL-адрес, на который отправляется запрос.
        payload (str, optional): Тело запроса. Defaults to "".
        headers (dict, optional): Заголовки запроса. Defaults to {}.

    Returns:
        str: Текст ответа, если запрос был успешным.
        None: Если запрос не был успешным.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload, timeout=500) as response:
            
            if response.status == 200:
                return await response.text()
            else:
                print(response.status)
                return response.status
