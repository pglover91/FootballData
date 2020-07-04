import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import argparse


def get_args():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = 'Scraper',
        epilog = ''
    )

    parser.add_argument(
        '--league',
        help = 'BBC sport league name',
        metavar = '<league>',
        dest = 'league',
        required = True
    )

    args = parser.parse_args()

    return args


class Scraper(object):
    def __init__(self, league):
        self.league = league
        print(league)

    def execute(self):
        """ Run class methods """
        url = "https://www.bbc.co.uk/sport/football/50106247"

        self.obtain_game_urls()
        self.create_card_dataset()

    def obtain_game_urls(self):
        """ Obtain game urls that have been played """
        home_url = "https://www.bbc.co.uk/sport/football/{}/scores-fixtures/2019-{}"
        start = 8
        month = 12

        cols = ['month', 'url', 'url_number', 'fixture']
        df = pd.DataFrame()

        for n in range(start, month+1):
            month = datetime.date(1900, int(n), 1).strftime('%B')

            n = str(n)
            if len(n) == 1:
                n = "0{}".format(n)
            url = home_url.format(self.league, f'{n}?filter=results')
            print('Scraping fixture urls from {}'.format(url))

            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            links = soup.find_all("a", {"class": "sp-c-fixture__block-link"})

            for link in links:

                teams = link.find_all("abbr", {"class": "gs-u-display-block gs-u-display-none@m sp-c-fixture__team-name-trunc"})
                if len(teams) == 2:
                    h = teams[0]['title'].replace(' ','')
                    a = teams[1]['title'].replace(' ','')
                    fixture = "{}-{}".format(h,a)

                url = "https://www.bbc.co.uk{}".format(link['href'])
                url_number = int(url.split('/')[-1])
                df1 = pd.DataFrame(columns=cols, data=[[month, url, url_number, fixture]])
                df = df.append(df1)

        df = df.sort_values('url_number').reset_index(drop=True)
        df = df.loc[~(df['url'].str.contains('live'))]

        df = df[['url', 'fixture']].apply(
            self.extract_referee_and_check_full_time, axis=1)

        df = df.loc[(df['full_time'] == True)].drop('full_time', axis=1)

        self.fixture_df = df

    def extract_referee_and_check_full_time(self, row):
        """ Extrct referee from a game url and also assign True/False
        value for if the game has finished """
        url = row.url
        fixture = row.fixture
        print('Scraping referee data from {} ({})'.format(url, fixture))
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        full_time_result = soup.find_all("abbr", {"title": "Full Time"})
        if len(full_time_result) == 0:
            row['full_time'] = False
            row['referee'] = False
        else:
            try:
                ref_data = soup.find_all("dd")[0]
                referee = ref_data.contents[0]
                row['full_time'] = True
                row['referee'] = referee
            except:
                row['full_time'] = False
                row['referee'] = False
        return row

    def create_card_dataset(self):
        """ Create entire card dataset from games played """
        df = pd.DataFrame()
        # loop through fixtures
        for i, row in self.fixture_df.iterrows():
            print('{}/{}: Scraping card data from: {} ({})'.format(
                i, len(self.fixture_df), row.url, row.fixture))
            # append card data from extract_card_data() method to df
            df1 = self.extract_card_data_per_game(row)
            df = df.append(df1)


        cols = ['team', 'ground', 'yc', 'rc',  'yc_against',
            'total_yc', 'over_1_yc', 'over_2_yc',
            'over_1_yc_each_team', 'over_2_yc_each_team',
            'fixture', 'referee'
            ]

        df = df[cols].reset_index(drop=True)

        self.format_card_data_per_team(df)
        self.format_referee_card_data(df)

    def extract_card_data_per_game(self, row):
        """ Extract card data from url given as arg """
        url = row.url

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        cols = ['fixture', 'home_team', 'away_team',
            'home_team_yc', 'home_team_rc',
            'away_team_yc', 'away_team_rc', 'referee']
        df = pd.DataFrame()

        tables = soup.find_all("div", {"class": "gel-layout__item gel-1/2@s"})

        def find_card_count(row, count):
            if row.yc >= count and row.yc_against >= count:
                return True
            else:
                return False

        if len(tables) == 2:
            for n, table in enumerate(tables):
                team = table.find(class_="gs-u-mb gel-great-primer-bold"
                    ).contents[0]

                if n == 0:
                    home_team = team
                    ground =  'H'
                elif n == 1:
                    away_team = team
                    ground = 'A'

                yellow_card = table.find_all('i',
                    {"class": "sp-c-booking-card sp-c-booking-card--rotate "
                        "sp-c-booking-card--yellow gs-u-ml"})
                num_yellow_card = len(yellow_card)

                yellow_and_red_card = table.find_all('i',
                    {"class": "sp-c-booking-card sp-c-booking-card--rotate "
                        "sp-c-booking-card--yellow-red gs-u-ml"})
                num_yellow_and_red_card = len(yellow_and_red_card)

                red_card = table.find_all('i',
                    {"class": "sp-c-booking-card sp-c-booking-card--rotate "
                        "sp-c-booking-card--red gs-u-ml"})
                num_red_card = len(red_card)

                if num_yellow_and_red_card >= 1:
                    num_yellow_card = num_yellow_card + (num_yellow_and_red_card*2)
                    num_red_card = num_red_card + num_yellow_and_red_card

                columns = ['team', 'yc', 'rc', 'ground']

                data = [team, num_yellow_card, num_red_card, ground]

                df1 = pd.DataFrame(columns=columns, data=[data])
                df = df.append(df1)

                h = df['team'].loc[(df['ground'] == 'H')
                    ].to_string(index=False).replace(' ','')
                a = df['team'].loc[(df['ground'] == 'A')
                    ].to_string(index=False).replace(' ','')

                df['total_yc'] = df['yc'].sum()
                df['yc_against'] = df.apply(
                    lambda x: (x.total_yc - x.yc), axis=1)

                df['over_1_yc'] = df['yc'].apply(
                    lambda x: True if x >=1 else False)
                df['over_2_yc'] = df['yc'].apply(
                    lambda x: True if x >=2 else False)

                df['over_1_yc_each_team'] = df.apply(find_card_count,
                    count=1, axis=1)
                df['over_2_yc_each_team'] = df.apply(find_card_count,
                    count=2, axis=1)

                df['fixture'] = "{}-{}".format(h,a)
                df['referee'] = row.referee

            if not df.empty:
                # print(df[['team', 'ground', 'yc', 'rc', 'yc_against', 'total_yc', 'fixture']])
                # print(df1)
                return df

    def format_card_data_per_team(self, df):
        """ Format card data into total values per team """

        total_cols = ['team', 'total_yc', 'total_rc', 'total_yc_against',
            'pc_over_1_yc', 'pc_over_2_yc',
            'pc_over_1_yc_each_team', 'pc_over_2_yc_each_team',
            'games_played']
        total_df = pd.DataFrame(columns=total_cols)

        for team, df1 in df.groupby('team'):
            df1['games_played'] = len(df1)

            total_over_1_yc_each_team = df1['over_1_yc_each_team'].sum()
            total_over_2_yc_each_team = df1['over_2_yc_each_team'].sum()
            pc_over_1_yc_each_team = total_over_1_yc_each_team / len(df1)
            pc_over_2_yc_each_team = total_over_2_yc_each_team / len(df1)

            total_team_over_1_yc = df1['over_1_yc'].sum()
            total_team_over_2_yc = df1['over_2_yc'].sum()
            pc_team_over_1_yc = total_team_over_1_yc / len(df1)
            pc_team_over_2_yc = total_team_over_2_yc / len(df1)

            df2 = pd.DataFrame(
                columns=total_cols,
                data=[[team, df1['yc'].sum(), df1['rc'].sum(),
                    df1['yc_against'].sum(),
                    pc_team_over_1_yc, pc_team_over_2_yc,
                    pc_over_1_yc_each_team, pc_over_2_yc_each_team, len(df1)]]
            )
            total_df = total_df.append(df2)

        total_df = total_df[total_cols]
        print(total_df.sort_values('total_yc', ascending=False))
        total_df.sort_values('total_yc', ascending=False).to_csv('/home/paul/CardData/{}.csv'.format(self.league))

    def format_referee_card_data(self, df):
        """ Use referee data to create referee dataset of card freq """
        df = df[['referee', 'fixture', 'total_yc']].drop_duplicates()

        df['games_refereed'] = df.groupby('referee')['referee'].transform('count')


        df = df.groupby('referee').agg({
            'referee': 'first',
            'games_refereed': 'first',
            'total_yc': sum,
        }).reset_index(drop=True)

        df['yc_per_game'] = df.apply(lambda x: (x.total_yc / x.games_refereed), axis=1)

        df.to_csv('/home/paul/CardData/{}-referee.csv'.format(self.league))






if __name__ == '__main__':

    args = get_args()

    scraper = Scraper(league=args.league)
    scraper.execute()
