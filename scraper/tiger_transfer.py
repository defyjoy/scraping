import uuid
import logging
import pandas as pd
from io import StringIO
from datetime import date, timedelta
from bs4 import BeautifulSoup

from scraper import PipelineScraper

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class TigerTransfer(PipelineScraper):
    tsp = None
    tsp_name = None
    source = 'tigertransfer.energytransfer'
    api_url = 'https://tallgrassenergylp.trellisenergy.com/ptms/public/infopost/getInfoPostingHome.do'
    get_url = f'https://tigertransfer.energytransfer.com/ipost/TGR/capacity/operationally-available?max=ALL'
    download_csv_url = f'https://tigertransfer.energytransfer.com/ipost/TGR/capacity/operationally-available?max=ALL'
    tsp_info_element = "section.copy > h2"

    params = [
        ('f', 'csv'),
        ('extension', 'csv'),
        ('asset', 'FEP'),
        ('gasDay', date.today().strftime('%m/%d/%Y')),
        ('cycle', 1),
        ('searchType', 'NOM'),
        ('searchString', ''),
        ('locType', 'ALL'),
        ('locZone', 'ALL')
    ]

    def __init__(self, job_id):
        PipelineScraper.__init__(self, job_id, web_url=self.api_url, source=self.source)

    def get_tsp_info(self, soup: BeautifulSoup):
        tsp_tag = soup.select_one(self.tsp_info_element)
        tsp_text = list(map(str.strip, tsp_tag.text.split(',')))

        # 0th element is TSP Name
        tsp_name = tsp_text[0].split(':')[1].strip()

        # 1st element is TSP
        tsp = tsp_text[1].split(':')[1].strip().replace(')', '')

        posting_info = soup.select("section.copy > p.pad")
        # 0th element is post datetime
        post_datetime = list(
            map(str.strip, posting_info[0].text.split(sep=':', maxsplit=1)))[1]

        # 1st element is Effective Gas Day/Time
        effective_gas_datetime = list(
            map(str.strip, posting_info[1].text.split(sep=':', maxsplit=1)))[1]

        # 2nd element is Measurement Basis Description
        measurement_basis_description = list(
            map(str.strip, posting_info[2].text.split(sep=':', maxsplit=1)))[1]

        return tsp, tsp_name, post_datetime, effective_gas_datetime, measurement_basis_description

    def add_columns(self, df_data):
        response = self.session.get(self.get_url)
        soup = BeautifulSoup(response.text, 'lxml')

        tsp, tsp_name, post_datetime, effective_gas_datetime, measurement_basis_description = self.get_tsp_info(soup)

        df_data.insert(0, 'TSP', tsp, True)
        df_data.insert(1, 'TSP Name', tsp_name, True)
        df_data.insert(2, 'Post Date/Time', post_datetime, True)
        df_data.insert(3, 'Effective Gas Day/Time', effective_gas_datetime, True)
        df_data.insert(4, 'Meas Basis Desc', measurement_basis_description, True)

        return df_data

    def start_scraping(self, post_date: date = None):
        try:
            logger.info('Scraping %s pipeline gas for post date: %s', self.source, post_date)
            response = self.session.get(self.download_csv_url, params=self.params)
            response.raise_for_status()
            html_text = response.text
            csv_data = StringIO(html_text)
            df_result = pd.read_csv(csv_data)
            final_report = self.add_columns(df_result)
            self.save_result(final_report, post_date=post_date, local_file=True)

            logger.info('File saved. end of scraping: %s', self.source)
        except Exception as ex:
            logger.error(ex, exc_info=True)
        return None


def back_fill_pipeline_date():
    scraper = TigerTransfer(job_id=str(uuid.uuid4()))
    for i in range(90, -1, -1):
        post_date = (date.today() - timedelta(days=i))
        print(post_date)
        scraper.start_scraping(post_date)


def main():
    scraper = TigerTransfer(job_id=str(uuid.uuid4()))
    scraper.start_scraping()
    scraper.scraper_info()


if __name__ == '__main__':
    main()
