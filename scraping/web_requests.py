import requests, logging
from requests import Response

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# logger.setLevel(logging.DEBUG)


def get_req(url, headers):
    for _ in range(5):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                response.raise_for_status()
                return response
        except Exception as e:
            logger.error(e)
            continue
        print('Error status code', response.status_code, response.text)


def post_req(url, headers, data) -> Response:
    for _ in range(5):
        try:
            logger.info(f"🔥 Starting web requests. url: {url} ,headers: {headers}")
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            if response.history:
                logger.info("Request was redirected")
                for resp in response.history:
                    logger.info(resp.status_code, resp.url)
                logger.info("Final destination:")
                logger.info(response.status_code, response.url)
            else:
                return response
        except RuntimeError as re:
            raise
        except Exception as e:
            print(e)
            continue
        logger.info(f"Response status code  {response.status_code} {response.text}")
