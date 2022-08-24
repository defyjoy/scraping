from scrapers.ienovarosarito import IenovaRosarito
from scrapers.mountainwest import Mountainwest
from scrapers.tigertransfer import TigerTransfer
from functools import singledispatch
from scraping import *

urls = {
    "mountainwest":
        "https://pipeview.questar.com:8443/ords/f?p=560:11:::::P0_PIPELINE,P0_CYCLE,P0_REQUESTOR:MWP,1,WEB:",
    "ienova_rosarito":
        "https://gasoductos.avantgardportal.com/ipws/rest/external/livepostings?menuId=-5600002&ownerId=1020",
    "tigertransfer": "https://tigertransfer.energytransfer.com/ipost/TGR/capacity/operationally-available?max=ALL"
}


class Scraper:
    def __init__(self, args):
        self.args = args

    def scrape(self):
        start_scraping = {
            'mountainwest': self.scrape_mountainwest,
            'rosarito': self.scrape_ienova_rosarito,
            'tigertransfer': self.scrape_tigertransfer
        }.get(self.args.scrape)
        start_scraping()

    def scrape_mountainwest(self):
        mountainwest: SeleniumScrape = Mountainwest(
            url=urls[self.args.start_scrape]
            , days=1
            , drop_column_regex='Unnamed'
            , table_element_to_exist="table.t13Standard"
            , search_input_field="#P11_EFF_DATE"
            , search_button="Submit Report"
            , table_element_class=".t13Standard"
        )
        mountainwest.scrape()

    def scrape_ienova_rosarito(self):
        ienova_rosarito = IenovaRosarito(urls[self.args.scrape])
        ienova_rosarito.scrape()

    def scrape_tigertransfer(self):
        tiger_transfer = TigerTransfer(url=urls[self.args.scrape], days=1,
                                       html_table_element="#operationallyAvailableTable")
        tiger_transfer.start_scrape()


