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




#
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
#         help = 'Sofascore league name',
#         metavar = '<league>',
#         dest = 'league',
#         required = True
#     )
#
#     parser.add_argument(
#         '--country',
#         help = 'League country',
#         metavar = '<country>',
#         dest = 'country',
#         required = True
#     )
#
#     parser.add_argument(
#         '--number',
#         help = 'Sofascore league number',
#         metavar = '<number>',
#         dest = 'number',
#         required = True
#     )
#
#
#     args = parser.parse_args()
#
#     return args
#

class Scraper(object):
    def __init__(self):
        pass
        # self.league = args.league
        # self.country = args.country
        # self.number = args.number

    def execute(self):
        """ Run class methods """

        self.home = "https://www.sofascore.com/"

        self.get_league()

        # league_url = "https://www.sofascore.com/tournament/football/{country}/{league}/{number}"
        # self.league_url = league_url.format(country=self.country, league=self.league, number=self.number)
        # self.obtain_game_urls()
        # self.read_fixture_data()
        # self.format_team_card_data()

    def get_league(self):
        """ Get league """

        # page = requests.get(self.home)
        driver = webdriver.Firefox("/usr/local/bin/")
        driver.get(self.home)


        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'leagues')]")))
        elements = driver.find_elements_by_xpath(
            "//div[@class='leagues']//a[contains(@href,'england')]")
        elements = [e for e in elements if "amateur" not in str(e.get_attribute("href"))]
        for element in elements:
            print(element.get_attribute("href"))
            element.click()
            elements = driver.find_elements_by_xpath(
                "//div[@class='leagues']//a[contains(@href,'premier-league')]")
            for element in elements:
                print(element.get_attribute("href"))
                element.click()


                items = driver.find_elements_by_xpath(
                    ("//div[@class='cell cell--justified u-p8 u-bg u-border u-no-border-bottom js-select-events-by-week-container ']"
                    "//div[@class='cell__section--main u-tC u-pos-relative u-show-overflow']"
                    "//div[@class='dropdown dropdown-select']"
                    #"//button[contains(@class,'btn dropdown__toggle')]"
                    )
                )

                dropdown_class = ("dropdown-menu dropdown__menu "
                    "dropdown__menu--compact dropdown__menu--box-events "
                    "js-select-week-dropdown js-select-events-dropdown-inner "
                    "u-h400 ps-container")

                for i in items:
                    item_list = i.find_elements_by_xpath(
                            ("//ul[@class='{}']//li[@class='dropdown__item ']"
                            "//a[@class='pointer js-select-week-dropdown-item']"
                        ).format(dropdown_class))
                    for item in item_list:

                        option = item.find_elements_by_xpath(
                            "a[@data-week-index='1']"
                        )

                        print(option)

                        # option = item.get_attribute("innerHTML").replace(' ','').replace('\n','')
                        #
                        #
                        # if option == 'Week1':
                        #
                        #     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='pointer js-select-week-dropdown-item']")))
                        #     item.click()

                            # item.click()

                            # # driver.execute_script("arguments[0].scrollIntoView();", item)
                            # # WebDriverWait(driver, 1000).until(EC.element_to_be_clickable(
                            # #     (By.XPATH, "//a[@class='pointer js-select-week-dropdown-item]")))
                            # actions = ActionChains(driver)
                            # actions.move_to_element(item)
                            # item.click()

                            # button = item.find_elements_by_xpath("//button[@class='btn dropdown__toggle dropdown__toggle--compact']")[0]
                            # button.click()

        # driver.close()




    def obtain_game_urls(self):
        """ Obtain league games from league url """

        page = requests.get(self.league_url)
        soup = BeautifulSoup(page.content, "html.parser")

        data = soup.find_all("a", {"class": "pointer js-uniqueTournament-page-load-season"})

        for tag in data:
            if "19/20" in tag.contents[0]:
                league_json_id = tag['data-season-id']
                break

        league_json_url = "https://www.sofascore.com/u-tournament/{number}/season/{json_id}/json".format(
            number=self.number,
            json_id=league_json_id)
        print(league_json_url)


        cols = ['home_team', 'away_team', 'json_id']
        df = pd.DataFrame(columns=cols)

        r = requests.get(league_json_url)
        json_data = r.json()

        with open('league_data.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        x = 0
        for event in json_data['teamEvents']:
            for e in json_data['teamEvents'][event]:
                for n in json_data['teamEvents'][event][e]:
                    print(n)
                    for i in json_data['teamEvents'][event][e][n]:
                        x+=1
                        id = i['id']
                        # customId = i['customId']
                        home_team = i['homeTeam']['name']
                        away_team = i['awayTeam']['name']

                        print("{} vs {} ({})".format(home_team, away_team, id))
                        data = [home_team, away_team, id]
                        df = df.append(
                            pd.DataFrame(columns=cols, data=[data])
                        )
        print(x)
        #
        # for j in json_data['events']['weekMatches']['tournaments']:
        #     for d in j['events']:
        #         print(d['homeTeam']['name'])
        #         print(d['awayTeam']['name'])

        df = df.drop_duplicates().sort_values('json_id')

        print(df)

        self.fixture_df = df

    def read_fixture_data(self):
        """ Read fixture data """

        url = "https://www.sofascore.com/event/{}/json"

        df = self.fixture_df

        print(
                df.loc[(
                    (df['home_team'] == 'West Bromwich Albion') |
                    (df['away_team'] == 'West Bromwich Albion')
                )]
        )

        #
        # df = df.append(
        #     pd.DataFrame(
        #         columns=['home_team', 'away_team', 'json_id'],
        #         data=[['Arsenal', 'Burnley', 8243414]]
        #     )
        # )


        team_cols = ['fixture', 'home_team', 'home_yellow', 'home_red',
            'away_team', 'away_yellow', 'away_red']
        team_card_df = pd.DataFrame()

        player_cols = ['player', 'team', 'yellow', 'red']
        player_card_df = pd.DataFrame()

        for i, row in df.iterrows():

            r = requests.get(url.format(row.json_id))
            json_data = r.json()

            home_yellow, home_red, away_yellow, away_red = 0,0,0,0

            for incident in json_data['incidents']:
                try:
                    type = incident['type']
                    player = incident['player']['name']
                    team = incident['playerTeam']
                    if team == 1:
                        team = row.home_team
                        if type == 'Yellow':
                            home_yellow += 1
                        elif type == 'YellowRed':
                            home_yellow += 1
                            home_red += 1
                        elif type == 'Red':
                            home_red += 1

                    elif team == 2:
                        team = row.away_team
                        if type == 'Yellow':
                            away_yellow += 1
                        elif type == 'YellowRed':
                            away_yellow += 1
                            away_red += 1
                        elif type == 'Red':
                            away_red += 1
                    # print("Card: {}\nPlayer: {}\nTeam: {}\n".format(
                    #         type, player, team))

                    player_y = False
                    player_r = False
                    if type == 'Yellow':
                        player_y = True
                    elif type == 'YellowRed':
                        player_y, player_r = True, True
                    elif type == 'Red':
                        player_r = True

                    player_data = [player, team, player_y, player_r]
                    player_card_df = player_card_df.append(
                        pd.DataFrame(columns=player_cols, data=[player_data])
                    )

                except:
                    pass

            fixture = "{}-{}".format(row.home_team.replace(' ',''),
                row.away_team.replace(' ',''))

            team_data = [fixture,
                row.home_team, home_yellow, home_red,
                row.away_team, away_yellow, away_red]

            team_card_df = team_card_df.append(
                pd.DataFrame(
                    columns=team_cols,
                    data=[team_data]
                ))


        player_card_df['total_yc'] = player_card_df.groupby('player')['player'].transform('count')
        player_card_df['total_rc'] = player_card_df.groupby('player')['player'].transform('count')

        p_df = pd.DataFrame()

        for player, df1 in player_card_df.groupby('player'):
            total_yc = len(df1.loc[(df1['yellow'] == True)])
            total_rc = len(df1.loc[(df1['red'] == True)])

            team = df1['team'].drop_duplicates().to_string(index=False)

            p_df = p_df.append(
                pd.DataFrame(
                    columns=['player', 'team', 'total_yc', 'total_rc'],
                    data=[[player, team, total_yc, total_rc]]
                )
            )

        self.team_card_df = team_card_df

    def format_team_card_data(self):
        """ """
        df = self.team_card_df

        df['home_total_cards'] = df.apply(lambda x:
            x.home_yellow + x.home_red, axis=1)
        df['away_total_cards'] = df.apply(lambda x:
            x.away_yellow + x.away_red, axis=1)

        cols = ['team', 'total_cards_for', 'total_cards_against',
            'over_1_card_each_team', 'over_2_card_each_team', 'over_3_card_each_team',
            'over_1_cards', 'over_2_cards', 'over_3_cards',
        ]

        def find_card_count(row, count):
            if row.home_total_cards >= count and row.away_total_cards >= count:
                return True
            else:
                return False

        def extract_card_data(df, team):

            return_df = pd.DataFrame(columns=cols)

            team_loc = team.split('_')[0]
            if team_loc == 'home':
                other_team_loc = 'away'
            elif team_loc == 'away':
                other_team_loc = 'home'

            for t, df1 in df.groupby(team):

                df1 = df1[['{}_team'.format(team_loc), 'home_total_cards', 'away_total_cards']]

                df1['over_1_card_each_team'] = df1.apply(find_card_count,
                    count=1, axis=1)
                df1['over_2_card_each_team'] = df1.apply(find_card_count,
                    count=2, axis=1)
                df1['over_3_card_each_team'] = df1.apply(find_card_count,
                    count=3, axis=1)

                df1 = df1.rename(columns={
                    '{}_team'.format(team_loc): 'team',
                    '{}_total_cards'.format(team_loc): 'total_cards_for',
                    '{}_total_cards'.format(other_team_loc): 'total_cards_against'
                })

                df1['over_1_cards'] = df1['total_cards_for'].apply(
                    lambda x: True if x >=1 else False)
                df1['over_2_cards'] = df1['total_cards_for'].apply(
                    lambda x: True if x >=2 else False)
                df1['over_3_cards'] = df1['total_cards_for'].apply(
                    lambda x: True if x >=3 else False)

                return_df = return_df.append(df1)

            return return_df

        h_df = extract_card_data(df, 'home_team')
        a_df = extract_card_data(df, 'away_team')

        df = pd.concat([h_df, a_df])

        total_cols = ['team', 'total_cards_for', 'total_cards_against',
            'pc_over_1_card', 'pc_over_2_cards', 'pc_over_3_cards',
            'pc_over_1_card_each_team', 'pc_over_2_cards_each_team',
            'pc_over_3_cards_each_team',
            'games_played']
        total_df = pd.DataFrame(columns=total_cols)

        for team, df1 in df.groupby('team'):
            # df1['games_played'] = len(df1)

            total_over_1_card_each_team = df1['over_1_card_each_team'].sum()
            total_over_2_card_each_team = df1['over_2_card_each_team'].sum()
            total_over_3_card_each_team = df1['over_3_card_each_team'].sum()
            pc_over_1_card_each_team = total_over_1_card_each_team / len(df1)
            pc_over_2_card_each_team = total_over_2_card_each_team / len(df1)
            pc_over_3_card_each_team = total_over_3_card_each_team / len(df1)

            total_team_over_1_card = df1['over_1_cards'].sum()
            total_team_over_2_card = df1['over_2_cards'].sum()
            total_team_over_3_card = df1['over_3_cards'].sum()
            pc_team_over_1_card = total_team_over_1_card / len(df1)
            pc_team_over_2_card = total_team_over_2_card / len(df1)
            pc_team_over_3_card = total_team_over_3_card / len(df1)

            data = [team, df1['total_cards_for'].sum(),  df1['total_cards_against'].sum(),
                pc_team_over_1_card, pc_team_over_2_card, pc_team_over_3_card,
                pc_over_1_card_each_team, pc_over_2_card_each_team, pc_over_3_card_each_team,
                len(df1)]

            df2 = pd.DataFrame(
                columns=total_cols,
                data=[data]
            )
            total_df = total_df.append(df2)


        total_df = total_df[total_cols]
        print(total_df.sort_values('total_cards_for', ascending=False))







if __name__ == '__main__':

    # args = get_args()

    scraper = Scraper()
    scraper.execute()
