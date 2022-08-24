import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
from scraping import *
from pathlib import Path


class Mountainwest(SeleniumScrape):
    def __init__(self, url, drop_column_regex, days, table_element_to_exist: str
                 , search_input_field: str
                 , search_button: str
                 , table_element_class: str):
        super().__init__(url)
        today = datetime.today()
        date_days_ago = today - timedelta(days=days)

        self.drop_column_regex = drop_column_regex
        self.days = days
        self.table_element_to_exist = table_element_to_exist
        self.search_input_field = search_input_field
        self.search_button = search_button
        self.table_element_class = table_element_class
        self.date_list = pd.date_range(start=date_days_ago, end=datetime.today()).tolist()
        # self.scraper.py = type(self).__name__.lower()

    @profile
    def scrape(self):
        try:
            self.__scrape()
            print(f"🟩 Mountain west csv successfully exported to {datetime.today().strftime('%Y')} folder")
        except RuntimeError as e:
            print("Internal Server error")
            print(e)
        finally:
            print("✅Scraping completed")


    def __scrape(self):
        for date in self.date_list:
            self.__navigate(date)

    def __navigate(self, date: datetime):
        print("==> loading.......")
        wait_until(S(self.table_element_to_exist).exists)
        print("page load completed....")

        print("➡️ search input field.....")
        input_field = S(self.search_input_field)
        print("input field for search completed.....")

        print(f"🔎 search {date.strftime('%m/%d/%Y')} into the input field.....")
        write(date.strftime("%m/%d/%Y"), input_field)  # For example - "05/19/2022"

        print(f"*️⃣ click button: Search.......")
        click(Button(self.search_button))

        print("📄 data loading.......")
        wait_until(S(self.table_element_to_exist).exists)
        print("📑 data load complete.....")

        driver = get_driver()
        soup = BeautifulSoup(driver.page_source, "html.parser")
        html_table = soup.select_one(self.table_element_class)

        data_frame = self.__extract_data(html_table)
        self.__save_to_dir(data_frame, save_into_dir="csv", date=date)

    def __extract_data(self, table: BeautifulSoup) -> DataFrame:
        df = pd.read_html(str(table))[0]
        df = df[df.columns.drop(list(df.filter(regex=self.drop_column_regex)))]
        print(df)
        return df

    def __save_to_dir(self
                      , dataframe: DataFrame
                      , date: datetime
                      , save_into_dir: str):

        scraper = type(self).__name__.lower()
        try:
            year = date.strftime("%Y")
            month = date.strftime("%m")
            day = date.strftime("%d")

            path = os.path.join(os.getcwd(), scraper, year, month, day)
            Path(path).mkdir(parents=True, exist_ok=True)
            csv = os.path.join(path, f"{date.strftime('%Y-%m-%d')}.csv")
            dataframe.to_csv(csv)
        except RuntimeError:
            print(f"Could not save csv into {csv}")
        finally:
            print(f"Save to dir completed {csv}")
