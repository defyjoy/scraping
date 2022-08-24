from helium import *
from scrapers.mountainwest import Mountainwest
from helium import *
from scrapers.scraper import SeleniumScrape, Scraper


def main():
    """
    Example -
        python main.py --scrape mountainview
        python main.py --scrape rosarito

    :return:
    """
    import argparse

    parser = argparse.ArgumentParser(description='Create a parser schema')
    parser.add_argument('--scrape', metavar='path', required=True, help='the path to workspace')
    args = parser.parse_args()

    scraper = Scraper(args)
    scraper.scrape()


if __name__ == "__main__":
    main()
