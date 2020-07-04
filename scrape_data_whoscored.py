import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import argparse
import urllib, json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains














class Scraper(object):
    def __init__(self):
        pass
        # self.league = args.league
        # self.country = args.country
        # self.number = args.number

    def execute(self):
        """ Run class methods """

        self.home = "https://www.whoscored.com/"

        self.get_league()



    def get_league(self):

        page = requests.get(self.home)

        print(page)


        # page = requests.get(self.league_url)
        # soup = BeautifulSoup(page.content, "html.parser")











if __name__ == '__main__':

    # args = get_args()

    scraper = Scraper()
    scraper.execute()
