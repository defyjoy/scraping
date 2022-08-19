from helium import *
from portals.mountainwest import Mountainwest
from helium import *


def main():
    url = "https://pipeview.questar.com:8443/ords/f?p=560:11:::::P0_PIPELINE,P0_CYCLE,P0_REQUESTOR:MWP,1,WEB:"

    mountainwest = Mountainwest(
        url=url
        , drop_column_regex='Unnamed', days=30
        , table_element_to_exist="table.t13Standard"
        , search_input_field="#P11_EFF_DATE"
        , search_button="Submit Report"
        , table_element_class=".t13Standard"
    )
    mountainwest.scrape()


if __name__ == "__main__":
    main()
