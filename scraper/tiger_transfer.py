import uuid
import logging
import pandas as pd
from io import StringIO
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
import argparse
import requests
from requests import Response

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
    posting_info_element = "section.copy > p.pad"

    params = [
        ('f', 'csv'),
        ('extension', 'csv'),
        ('asset', 'FEP'),
        # ('gasDay', date.today().strftime('%m/%d/%Y')),
        # ('cycle', 5),
        ('searchType', 'NOM'),
        ('searchString', ''),
        ('locType', 'ALL'),
        ('locZone', 'ALL')
    ]

    def __init__(self, query_date: datetime, cycle: str, job_id: str):
        PipelineScraper.__init__(self, job_id, web_url=self.api_url, source=self.source)
        self.scrape_date = query_date
        self.cycle = cycle
        self.params.append(tuple(('gasDay', self.scrape_date.strftime("%m/%d/%Y"))))
        self.params.append(tuple(('cycle', self.cycle)))

    def get_tsp_info(self, soup: BeautifulSoup):
        # select the TSP tag and get data
        tsp_tag = soup.select_one(self.tsp_info_element)
        tsp_text = list(map(str.strip, tsp_tag.text.split(',')))

        # 0th element is TSP Name
        tsp_name = tsp_text[0].split(':')[1].strip()

        # 1st element is TSP
        tsp = tsp_text[1].split(':')[1].strip().replace(')', '')

        # select the posting info elements. Post Datetime / Eff gas day/time and Measurement basis description
        posting_info = soup.select(self.posting_info_element)

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
        data = {
            "gasDay": self.scrape_date.strftime("%m/%d/%Y"),
            "cycle": self.cycle,
            "searchType": "NOM",
            "searchString": "",
            "locType": "ALL",
            "locZone": "ALL"
        }

        response = self.session.post(self.download_csv_url, data=data)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        tsp, tsp_name, post_datetime, effective_gas_datetime, measurement_basis_description = self.get_tsp_info(soup)

        df_data.insert(0, 'TSP', tsp, True)
        df_data.insert(1, 'TSP Name', tsp_name, True)
        df_data.insert(2, 'Post Date/Time', post_datetime, True)
        df_data.insert(3, 'Effective Gas Day/Time', effective_gas_datetime, True)
        df_data.insert(4, 'Meas Basis Desc', measurement_basis_description, True)

        return df_data

    def start_scraping(self, post_date: date = None):
        try:
            logger.info('Scraping %s pipeline gas for post date: %s', self.source, self.scrape_date)
            response = self.session.post(self.download_csv_url, data=self.params)
            response.raise_for_status()
            html_text = response.text
            csv_data = StringIO(html_text)
            df_result = pd.read_csv(csv_data)
            final_report = self.add_columns(df_result)
            self.save_result(final_report, post_date=self.scrape_date, local_file=True)

            logger.info('File saved. end of scraping: %s', self.source)
        except Exception as ex:
            logger.error(ex, exc_info=True)
        return None


def back_fill_pipeline_date():
    scraper = TigerTransfer(job_id=str(uuid.uuid4()))
    for i in range(90, -1, -1):
        post_date = (date.today() - timedelta(days=i))
        scraper.start_scraping(post_date)


def main():
    parser = argparse.ArgumentParser(description='Create a parser schema')
    parser.add_argument('--date', metavar='path', nargs='?', default=str(date.today()),
                        help='date for scraping.default is today(current date)')
    parser.add_argument('--cycle', metavar='path', nargs='?', default=5, help='cycle for scraping. default is final=5')

    args = parser.parse_args()

    query_date = datetime.fromisoformat(args.date) if args.date is not None else date.today()
    cycle = args.cycle
    scraper = TigerTransfer(query_date=query_date, cycle=cycle, job_id=str(uuid.uuid4()))
    scraper.start_scraping()
    scraper.scraper_info()


if __name__ == '__main__':
    main()
