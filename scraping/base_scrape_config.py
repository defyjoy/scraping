import logging
import os
from pandas import DataFrame
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from requests import Response

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BaseScrapeConfig:
    def __init__(self, html_table_element, save_folder):
        self.save_folder = save_folder
        self.html_table_element = html_table_element

    def scrape(self, response: Response, date: datetime):
        soup = BeautifulSoup(response.content, "html.parser")
        html_table = soup.select_one(self.html_table_element)
        data_frame = self.extract_data(html_table)
        self.save_scrape_output(dataframe=data_frame, date=date)

    def save_scrape_output(self, dataframe: DataFrame, date: datetime):
        scraper = type(self).__name__.lower()
        file_name = f"{date.strftime('%Y-%m-%d')}.csv"
        try:
            year = date.strftime("%Y")
            month = date.strftime("%m")
            day = date.strftime("%d")

            path = os.path.join(os.getcwd(), self.save_folder, scraper, year, month, day)
            Path(path).mkdir(parents=True, exist_ok=True)
            csv = os.path.join(path, file_name)
            dataframe.to_csv(csv)
        except RuntimeError as e:
            logging.error(f"Could not save csv into {file_name}")
            logger.error(e.__str__())
        finally:
            logger.info(f"✅ Save to dir completed {file_name}")

    def extract_data(self, table: BeautifulSoup) -> DataFrame:
        df = pd.read_html(str(table))[0]
        # df = df[df.columns.drop(list(df.filter(regex=self.drop_column_regex)))]
        return df
