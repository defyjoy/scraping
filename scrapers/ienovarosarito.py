from scraping import *
import jsonpickle, json
from scrapers.rosarito.rosarito_response import RosaritoResponse

class IenovaRosarito:
    def __init__(self, url):
        self.url = url

    def scrape(self):
        response = get_req(self.url, headers={})
        json_response = json.dumps(response.content.decode('utf-8'))
        print(json_response)
        thawed = jsonpickle.decode(json_response)
        # print(thawed)
        result: list[RosaritoResponse] = jsonpickle.decode(thawed, keys=True, classes=list[RosaritoResponse])
        print(result[0])
        for item in result:
            print(item.posting_id)
