import requests


def get_req(url, headers):
    for _ in range(5):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                return response
        except Exception as e:
            print(e)
            continue
        print('Error status code', response.status_code, response.text)
