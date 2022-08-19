import pandas as pd
import os
from helium import *
from bs4 import BeautifulSoup
from pandas import DataFrame
from datetime import datetime
from scraping import *


# from scraping import Scrape


class Mountainwest(Scrape):
    def __init__(self, url):
        super().__init__(url)

    def navigate(self
                 , table_element_to_exist: S
                 , search_input_field: S
                 , search_text: str
                 , search_button: Button
                 , table_element_class: str) -> BeautifulSoup:

        try:
            print("==> loading.......")
            wait_until(table_element_to_exist.exists)
            print("page load completed....")

            print("➡️ search input field.....")
            input_field = search_input_field
            print("input field for search completed.....")

            print(f"🔎 search {search_text} into the input field.....")
            write(search_text, input_field)

            print(f"*️⃣ click button: Search.......")
            click(search_button)

            print("📄 data loading.......")
            wait_until(table_element_to_exist.exists)
            print("📑 data load complete.....")

            driver = get_driver()
            soup = BeautifulSoup(driver.page_source, "html.parser")
            html_table = soup.select_one(table_element_class)
            return html_table
        except RuntimeError as e:
            print("Internal Server error")
            print(e)
        finally:
            print("Return dataframe")

    def extract_data(self
                     , table: BeautifulSoup
                     , drop_column_regex: str) -> DataFrame:
        df = pd.read_html(str(table))[0]
        df = df[df.columns.drop(list(df.filter(regex=drop_column_regex)))]
        print(df)
        return df

    def save_to_dir(self
                    , dataframe: DataFrame
                    , save_into_dir: str):
        try:
            csv_filename = datetime.today().strftime("%m-%d-%y")
            csv_dir = os.path.join(os.getcwd(), save_into_dir)

            if not os.path.exists(csv_dir):
                os.mkdir(csv_dir)

            csv = os.path.join(csv_dir, f"{csv_filename}.csv")

            dataframe.to_csv(csv)
        except RuntimeError:
            print(f"Could not save csv into {save_into_dir}")
        finally:
            print(f"Save to dir completed {csv_filename}")
