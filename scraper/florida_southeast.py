import io
import logging
import uuid
from datetime import datetime, date

import pandas as pd
from requests import HTTPError

from scraper import PipelineScraper

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class FloridaSouthEast(PipelineScraper):
    source = "fsc.nexteraenergyresources.com"
    source_extensions = ['vgt', 'mgt', 'gpl']
    api_url = 'https://fsc.nexteraenergyresources.com/'
    get_request_url = 'https://fsc.nexteraenergyresources.com/ptms/public/infopost/getInfoPostRpts.do'
    post_url = 'https://fsc.nexteraenergyresources.com/ptms/public/infopost/getInfoPostRptExportCsvFile.do'
    download_csv_url = 'https://fsc.nexteraenergyresources.com/ptms/public/infopost/getInfoPostRptExportCsvFile.do'

    init_request_params = [
        ("tspId", 1),
        ("rptId", 2),
        ("downloadInd", 0),
        ("searchInd", 0),
        ("showLatestInd", 0),
        ("cycleId", 10301),
        ("_search", "false"),
        ("rows", 100000),
        ("page", 1)
    ]

    def __init__(self, job_id):
        PipelineScraper.__init__(self, job_id, web_url=self.api_url, source=self.source)

    def set_request_params_date(self, post_date: date):
        self.init_request_params.append(tuple(('startDate', post_date.strftime("%m/%d/%Y"))))
        self.init_request_params.append(tuple(('endDate', post_date.strftime("%m/%d/%Y"))))

    def add_columns(self, df_tsp_data, df_data):
        df_data.insert(0, "TSP", df_tsp_data['TSP'].values[0], True)
        df_data.insert(1, "TSP Name", df_tsp_data['TSP Name'].values[0], True)
        df_data.insert(2, 'Posting Date/Time', df_tsp_data['Posting Date/Time'].values[0], True)
        df_data.insert(3, 'Eff Gas Day', df_tsp_data['Eff Gas Day'].values[0], True)
        df_data.insert(4, 'Meas Basis Desc', df_tsp_data['Meas Basis Desc'].values[0], True)
        return df_data

    def start_scraping(self, post_date: date = None):
        post_date = post_date if post_date is not None else date.today()
        try:
            logger.info('Scraping %s pipeline gas for post date: %s', self.source, post_date)
            self.set_request_params_date(post_date=post_date)

            # Start the request for json response
            response = self.session.get(self.get_request_url, params=self.init_request_params)
            response.raise_for_status()
            res_json = response.json()
            info_post_data_id = res_json['rows'][0]['id']
            response = self.session.get(self.download_csv_url, params=[('infoPostDataId', info_post_data_id)])

            str_data = str(response.content, 'utf-8')
            tsp_data = io.StringIO(str_data.split('\n\n')[0])

            df_tsp_result = pd.read_csv(tsp_data)
            df_tsp_result = df_tsp_result.dropna(how='all', axis=1)

            csv_data = io.StringIO(str_data.split('\n\n')[1])
            df_result = pd.read_csv(csv_data)
            df_result = df_result.dropna(how='all', axis=1)

            final_result = self.add_columns(df_tsp_data=df_tsp_result, df_data=df_result)
            self.save_result(final_result, post_date=post_date, local_file=True)

            logger.info('File saved. end of scraping: %s', self.source)

        except HTTPError as ex:
            logger.error(ex, exc_info=True)
        return None


def main():
    query_date = datetime.fromisoformat("2022-09-26")

    # there are no cycles to choose from in OneOK websites
    scraper = FloridaSouthEast(job_id=str(uuid.uuid4()))
    scraper.start_scraping(post_date=query_date)
    scraper.scraper_info()


if __name__ == '__main__':
    main()
