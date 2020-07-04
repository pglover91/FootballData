import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import argparse
# from selenium import webdriver


# def get_args():
#
#     parser = argparse.ArgumentParser(
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         description = 'Scraper',
#         epilog = ''
#     )
#
#     parser.add_argument(
#         '--league',
#         help = 'BBC sport league name',
#         metavar = '<league>',
#         dest = 'league',
#         required = True
#     )
#
#     args = parser.parse_args()
#
#     return args


class Scraper(object):
    def __init__(self):
        pass

    def execute(self):
        """ Run class methods """
        url = "https://int.soccerway.com/national/england/premier-league/20192020/regular-season/r53145/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        links = soup.find_all("table", {"class": "matches"})

        # driver = webdriver.Firefox("/usr/local/bin/")

        for link in links:
            row = link.find_all("tr")


            a = link.find_all("td", {"class": "team team-a"})
            b = link.find_all("td", {"class": "team team-b"})

            print(len(a))

            for i in range(len(a)):
                # match = "{} - {}"
                # weekmatch = match.format(a[i], b[i])
                # print(weekmatch)

                home_team = a[i].find('a').get('title')
                away_team = b[i].find('a').get('title')


                print("{} - {}".format(home_team, away_team))






if __name__ == '__main__':

    # args = get_args()

    # scraper = Scraper(league=args.league)
    scraper = Scraper()
    scraper.execute()
