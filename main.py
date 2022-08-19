from helium import *
from portals.moutainwest_pipeline import Mountainwest
from helium import *


def main():
    url = "https://pipeview.questar.com:8443/ords/f?p=560:11:::::P0_PIPELINE,P0_CYCLE,P0_REQUESTOR:MWP,1,WEB:"

    mountainwest = Mountainwest(url)

    table = mountainwest.navigate(
        table_element_to_exist=S("table.t13Standard")
        , search_text="05/19/2022"
        , search_button=Button("Submit Report")
        , search_input_field=S("#P11_EFF_DATE")
        , table_element_class=".t13Standard")

    df = mountainwest.extract_data(table=table, drop_column_regex='Unnamed')
    mountainwest.save_to_dir(dataframe=df, save_into_dir="csv")


if __name__ == "__main__":
    main()
