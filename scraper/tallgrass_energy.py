import uuid
import logging
import xmltodict
import pandas as pd
import argparse
from datetime import date, timedelta, datetime
from nested_lookup import nested_lookup

from scraper import PipelineScraper

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class TallgrassEnergy(PipelineScraper):
    tsp = None
    tsp_name = None
    source = 'tallgrassenergylp.trellisenergy'
    api_url = 'https://tallgrassenergylp.trellisenergy.com'
    post_url = 'https://tallgrassenergylp.trellisenergy.com//ptms/public/infopost/getInfoPostRpts.do'
    download_csv_url = f'https://tallgrassenergylp.trellisenergy.com/ptms/public/infopost/getInfoPostRptTxtFile.do'

    query_params_payload = [
        ('tspId', 1),
        ('proxyTspId', 1),
        ('rptId', 2),
        ('downloadInd', 0),
        ('searchInd', 0),
        ('showLatestInd', 0),
        ('nd', 1661953188765),
        ('_search', 'false'),
        ('rows', '10000'),
        ('page', '1')
    ]

    def __init__(self, job_id):
        PipelineScraper.__init__(self, job_id, web_url=self.api_url, source=self.source)
        # self.scrape_date = query_date
        # self.cycle = cycle
        # self.query_params_payload.append(tuple(('startDate', self.scrape_date.strftime("%m/%d/%Y"))))
        # self.query_params_payload.append(tuple(('endDate', self.scrape_date.strftime("%m/%d/%Y"))))
        # self.query_params_payload.append(tuple(('cycleId', self.cycle)))

    def add_columns(self, df_data, data_json):
        tsp, tsp_name, post_datetime, effective_gas_datetime, measurement_basis_description = self.get_tsp_info(
            data_json=data_json)
        df_data.insert(0, "tsp", tsp, True)
        df_data.insert(1, "tsp_name", tsp_name, True)
        df_data.insert(2, 'post_datetime', post_datetime, True)
        df_data.insert(3, 'effective_gas_datetime', effective_gas_datetime, True)
        df_data.insert(4, 'measurement_basis_description', measurement_basis_description, True)
        return df_data

    def get_tsp_info(self, data_json):
        print(data_json)
        columns = nested_lookup(key='name', document=data_json)
        data = nested_lookup('content', data_json['dictionaryKvpairs'])

        df = pd.DataFrame(data=[data], columns=columns)
        if df.empty:
            raise ValueError(
                "Additional Information cannot be provided. Could not find the information.Cannot proceed forward")

        # 0th element is TSP Name
        tsp_name = df['TSP Name'].iat[0]

        # 1st element is TSP
        tsp = df['TSP'].iat[0]

        # 0th element is post datetime
        post_datetime = df['Posting Date/Time'].iat[0]

        # 1st element is Effective Gas Day/Time
        effective_gas_datetime = df['Eff Gas Day'].iat[0]

        # 2nd element is Measurement Basis Description
        measurement_basis_description = df['Meas Basis Desc'].iat[0]
        return tsp, tsp_name, post_datetime, effective_gas_datetime, measurement_basis_description

    def start_scraping(self, post_date: date = None, cycle: int = None):
        try:
            logger.info('Scraping %s pipeline gas for post date: %s', self.source, post_date)

            self.query_params_payload.append(tuple(('startDate', post_date.strftime("%m/%d/%Y"))))
            self.query_params_payload.append(tuple(('endDate', post_date.strftime("%m/%d/%Y"))))
            self.query_params_payload.append(tuple(('cycleId', cycle)))

            response = self.session.post(self.post_url, params=self.query_params_payload)
            response.raise_for_status()
            response_json = response.json()
            print(response.request.url)
            print(response_json)

            if len(response_json['rows']) == 0:
                raise SystemExit("NO DATA FOUND")
            columns = response_json['rows']
            request_ids = [x['id'] for x in response_json['rows']]
            print(request_ids)

            for req_id in request_ids:
                query_params_payload = [
                    ('infoPostDataId', req_id)
                ]

                response = self.session.post(url=self.download_csv_url, params=query_params_payload)

                data_json = response.json()
                columns = [column['content'] for column in data_json['columnNames']]
                xml_json = xmltodict.parse(data_json['xmlData'])
                df_data = [cell['cell'] for cell in xml_json['rows']['row']]

                df_result = pd.DataFrame(data=df_data, columns=columns)
                final_report = self.add_columns(df_data=df_result, data_json=data_json)
                self.save_result(final_report, post_date=post_date, local_file=True)
                logger.info('File saved. end of scraping: %s', self.source)
        except Exception as ex:
            logger.error(ex, exc_info=True)
        return None


def back_fill_pipeline_date():
    scraper = TallgrassEnergy(job_id=str(uuid.uuid4()))
    for i in range(90, -1, -1):
        post_date = (date.today() - timedelta(days=i))
        print(post_date)
        scraper.start_scraping(post_date)


def main():
    # parser = argparse.ArgumentParser(description='Create a parser schema')
    # parser.add_argument('--date', metavar='path', nargs='?', default=str(date.today()),
    #                     help='date for scraping.default is today(current date)')
    # parser.add_argument('--cycle', metavar='path', nargs='?', default=10301,
    #                     help='cycle for scraping.default is final=5')
    #
    # args = parser.parse_args()
    #
    # query_date = datetime.fromisoformat(args.date) if args.date is not None else date.today()
    # cycle = args.cycle

    query_date = datetime.fromisoformat("2022-08-30")
    cycle = 10301

    scraper = TallgrassEnergy(job_id=str(uuid.uuid4()))
    scraper.start_scraping(post_date=query_date, cycle=cycle)
    scraper.scraper_info()


if __name__ == '__main__':
    main()
