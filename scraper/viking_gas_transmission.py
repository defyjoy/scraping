import uuid
import logging
import xmltodict
import pandas as pd
from io import StringIO
import argparse
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from nested_lookup import nested_lookup
from scraper import PipelineScraper

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class VikingGasTransmission(PipelineScraper):
    source = "vikinggastransmission.vgt.nborder"
    api_url = 'https://www.oneok.com'
    post_url = 'https://www.oneok.com/vgt/informational-postings/capacity/operationally-available'
    download_csv_url = 'https://www.oneok.com/vgt/informational-postings/capacity/operationally-available'

    html_header_css = ".rgHeaderDiv .rgMasterTable"
    html_table_css = ".rgDataDiv > .rgMasterTable"
    params = []

    def __init__(self, job_id):
        PipelineScraper.__init__(self, job_id, web_url=self.api_url, source=self.source)

    def get_headers(self, soup: BeautifulSoup):
        theads = soup.find_all("th", {"class": "rgHeader"})
        headers = [th.findNext("a").text for th in theads]
        return headers

    def start_scraping(self, post_date: date = None):
        try:
            logger.info('Scraping %s pipeline gas for post date: %s', self.source, post_date)
            self.params.append(
                tuple(('content_1$dcDateControls$rdpStartDate', post_date.strftime("%m/%d/%Y"))))
            self.params.append(
                tuple(('content_1$dcDateControls$rdpStartDate$dateInput', post_date.strftime("%m/%d/%Y"))))

            self.params.append(
                tuple(('content_1_dcDateControls_rdpStartDate_calendar_SD', [[2022, 8, 11]])))

            self.params.append(
                tuple(('content_1$dcDateControls$rdpEndDate', post_date.strftime("%m/%d/%Y"))))
            self.params.append(
                tuple(('content_1$dcDateControls$rdpEndDate$dateInput', post_date.strftime("%m/%d/%Y"))))

            self.params.append(
                tuple(('content_1_dcDateControls_rdpEndDate_calendar_SD', [[2022, 8, 11]])))


            response = self.session.post(self.download_csv_url, data=self.params)
            response.raise_for_status()
            print(response.status_code)

            soup = BeautifulSoup(response.content, 'lxml')

            headers = self.get_headers(soup)

            df_result = pd.read_html(str(soup.select_one(self.html_table_css)), na_values='')[0]
            df_result.columns = headers
            final_report = self.add_columns(soup=soup, df_result=df_result)
            self.save_result(df_result, post_date=post_date, local_file=True)
        except Exception as ex:
            logger.error(ex, exc_info=True)
        return None

    def add_columns(self, soup, df_result):
        tsp = soup.select_one("#content_1_CompanyName").text
        tsp_name = soup.select_one("#content_1_CompanyDUNS").text
        df_result.insert(0, 'TSP', tsp, True)
        df_result.insert(1, 'TSP Name', tsp_name, True)
        return df_result


def main():
    query_date = datetime.fromisoformat("2022-08-11")

    scraper = VikingGasTransmission(job_id=str(uuid.uuid4()))
    scraper.start_scraping(post_date=query_date)
    scraper.scraper_info()


if __name__ == '__main__':
    main()
