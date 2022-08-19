import time
from telnetlib import EC

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ChromeOptions
from .web_requests import get_req
import os

from helium import *


class Scrape(object):
    def __init__(self, url):
        """

        :param url: parameter for starting the chrome headless browser
        """
        self.url = url
        print("Base class init has been called")
        try:
            path = '{}:{}'.format(os.getenv('PATH'), "/opt/homebrew/lib/node_modules/webdriver-manager/selenium/")
            os.environ["PATH"] = path
            start_chrome(self.url, headless=True)
        except RuntimeError:
            print("Started Chrome Driver")
        finally:
            print("Run this always")

