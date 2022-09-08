import pathlib
from datetime import datetime, date
from pandas import DataFrame
import logging
from requests.adapters import HTTPAdapter, Retry

import numpy
import requests

LOCAL_DATA_FOLDER = './DATA'
logger = logging.getLogger(__name__)


class PipelineScraper:
    _output_folder = f'{LOCAL_DATA_FOLDER}/scraper_output'
    pathlib.Path(_output_folder).mkdir(parents=True, exist_ok=True)
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])

    def __init__(self, job_id, web_url, source, **kwargs):
        self.job_id = job_id
        self.web_url = web_url
        self.source = source
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=self.retries))

    def scraper_info(self):
        logger.info('Scraper: %s, web url: %s, job_id: %s', self.source, self.web_url, self.job_id)

    def _get_local_output_file_path(self, post_date: date):
        if post_date is None:
            post_date = date.today()
        _file_name = f'{self._output_folder}/{self.source}_data_{post_date.strftime("%Y-%m-%d")}_{datetime.now().timestamp()}.csv'
        return _file_name

    def save_result(self, df_result: DataFrame, post_date: date, db_table_name: str = None,
                    local_file: bool = False):
        """
        :param df_result:
        :param post_date:
        :param db_table_name:
        :param local_file:
        :return:
        """
        logger.info('Saving data for the source: %s', self.source)

        df_result.replace({numpy.nan: None}, inplace=True)
        logger.info('\n%s', df_result.count())
        if local_file:
            _file_path = self._get_local_output_file_path(post_date)
            logger.info('Saving data to file: %s', _file_path)
            df_result.to_csv(_file_path, index=False)
            logger.info('Scraping data saved to file: %s', _file_path)

        if db_table_name:
            logger.info('Saving data to database table: %s', db_table_name)

    def start_scraping(self, post_date: date = None):
        pass
