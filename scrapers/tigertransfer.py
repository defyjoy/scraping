from scraping import *
from datetime import datetime, timedelta
import pandas as pd
from scraping.base_scrape_config import BaseScrapeConfig

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
save_folder = "./DATA/scraper_output"


class TigerTransfer(BaseScrapeConfig):

    def __init__(self, url, days, html_table_element):
        super().__init__(html_table_element, save_folder)
        today = datetime.today()
        date_days_ago = today - timedelta(days=days)
        self.date_list = pd.date_range(start=date_days_ago, end=datetime.today()).tolist()

        self.url = url
        self.days = days
        self.html_table_element = html_table_element

    def start_scrape(self):
        try:
            for date in self.date_list:
                self.__navigate(date)
        except RuntimeError as e:
            logger.error(f"❌ tigertranfer csv successfully exported to {datetime.today().strftime('%Y')} folder")
            logger.error(e)
        finally:
            logger.info(f"✅ Scraping completed. Files saved in {save_folder}/{type(self).__name__.lower()}")

    def __navigate(self, date: datetime):
        data = {
            "gasDay": date.strftime("%m/%d/%Y"),
            "cycle": "0",
            "searchType": "NOM",
            "searchString": "",
            "locType": "ALL",
            "locZone": "ALL"
        }
        response = post_req(url=self.url, headers={}, data=data)
        self.scrape(response=response, date=date)
