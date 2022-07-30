import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime
from celery import shared_task
from .models import Prediction
from scipy.stats import poisson
import numpy as np
import os

options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1400,1500")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)


@shared_task
def ScrapeResult():
    urls = [
        'https://www.flashscore.com/football/belarus/vysshaya-liga',
        'https://www.flashscore.com/football/brazil/serie-a',
        'https://www.flashscore.com/football/argentina/liga-profesional',
        'https://www.flashscore.com/football/usa/mls',
        'https://www.flashscore.com/football/norway/eliteserien',
        'https://www.flashscore.com/football/china/super-league',
        'https://www.flashscore.com/football/japan/j1-league',
        'https://www.flashscore.com/football/egypt/premier-league',
        'https://www.flashscore.com/football/sweden/allsvenskan',
        'https://www.flashscore.com/football/norway/obos-ligaen',
        'https://www.flashscore.com/football/sweden/superettan',


    ]

    for url in urls:
        all_matches = []
        all_leagues = []
        predictions = []

        league = (url[36:39]).upper()

        driver.get(f'{url}/results/')
        max_show = 3
        count = 0
        while count <= max_show:
            try:
                show_more = driver.find_element(
                    By.LINK_TEXT, 'Show more matches')
                time.sleep(5)
                show_more.click()
                count += 1
            except:
                print('done')
                break
        time.sleep(5)
        matches = driver.find_elements(
            By.XPATH, '//div[@title="Click for match detail!"]')
        for match in matches:

            try:
                date = match.find_element(
                    By.CLASS_NAME, 'event__time').text[0:5]
            except:
                print('no date')

            try:
                hometeam = match.find_element(
                    By.CLASS_NAME, 'event__participant--home').text
            except:
                print('no hometeam')
            try:
                awayteam = match.find_element(
                    By.CLASS_NAME, 'event__participant--away').text
            except:
                print('no awayteam')
            try:
                homescore = match.find_element(
                    By.CLASS_NAME, 'event__score--home').text
            except:
                print('no homescore')
            try:
                awayscore = match.find_element(
                    By.CLASS_NAME, 'event__score--away').text
            except:
                print('no awayscore')

            result = [date, hometeam, awayteam, homescore,
                      awayscore]
            all_matches.append(result)
        try:
            country = driver.find_element(By.CLASS_NAME, 'heading__name').text
        except:
            print('country')

        df = pd.DataFrame(all_matches, columns=[
            'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        df.loc[df['FTHG'] > df['FTAG'], 'FTR'] = 'H'
        df.loc[df['FTHG'] == df['FTAG'], 'FTR'] = 'D'
        df.loc[df['FTHG'] < df['FTAG'], 'FTR'] = 'A'
        df['Country'] = country
        df['FTHG'] = df['FTHG'].astype(int)
        df['FTAG'] = df['FTAG'].astype(int)
        print('result scrappng concluded')
        time.sleep(5)


        # scrape for fixture

        driver.get(f'{url}/fixtures/')
        all_fixtures = []
        matches = driver.find_elements(
            By.CLASS_NAME, 'event__match--scheduled')[0:14]

        for match in matches:

            try:
                a = match.find_element(By.CLASS_NAME, 'event__time').text
                print(a)

                
            except:
                print('No date')
            try:
                hometeam = match.find_element(
                    By.CLASS_NAME, 'event__participant--home').text
            except:
                print('No hometeam')
            try:
                awayteam = match.find_element(
                    By.CLASS_NAME, 'event__participant--away').text
            except:
                print('No awayteam')

            day=a[0:2]
            mnth=a[3:5]
            hm=a[6:12]
            year='2022'
            date= f'{year}-{mnth}-{day}{hm}'
            
            fix = [date, hometeam, awayteam]
            all_fixtures.append(fix)

        fixtures = pd.DataFrame(all_fixtures, columns=[
                                'Date', 'HomeTeam', 'AwayTeam'])
        print('fixture scrappng concluded')

        time.sleep(5)

        data = df
        f = df.AwayTeam
        f = f.drop_duplicates()
        teams = f.to_list()
        result_home = []
        result_away = []
        for team in teams:
            FT = df.loc[df['HomeTeam'] == team]
            try:
                W = FT.FTR.value_counts().H
            except:
                W = 0
            try:
                D = FT.FTR.value_counts().D
            except:
                D = 0

            try:
                L = FT.FTR.value_counts().A
            except:
                L = 0

            try:
                Mp = FT.HomeTeam.count()
            except:
                Mp = 0

            try:
                Gs = FT.FTHG.sum()
            except:
                Gs = 0
            try:
                Gc = FT.FTAG.sum()
            except:
                Gc = 0

            r = [Mp, W, D, L, Gs, Gc]
            result_home.append(r)

        for team in teams:
            FT = df.loc[df['AwayTeam'] == team]
            try:
                L = FT.FTR.value_counts().H
            except:
                L = 0
            try:
                D = FT.FTR.value_counts().D
            except:
                D = 0

            try:
                W = FT.FTR.value_counts().A
            except:
                W = 0

            try:
                Mp = FT.AwayTeam.count()
            except:
                Mp = 0

            try:
                Gs = FT.FTAG.sum()
            except:
                Gs = 0
            try:
                Gc = FT.FTHG.sum()
            except:
                Gc = 0
            r = [Mp, W, D, L, Gs, Gc]
            result_away.append(r)

        teams_series = teams
        team = pd.DataFrame(teams_series, columns=['Team'])
        team

        home_series = result_home
        home = pd.DataFrame(home_series, columns=[
                            'P', 'W', 'D', 'L', 'GS', 'GC'])


        home['GD'] = home.GS - home.GC
        home['PTS'] = (home.W*3)+home.D
        home['AGS'] = (home.GS)/home.P
        home['AGC'] = (home.GC)/home.P
        average_goal_scored_home = home.GS.sum()/home.P.sum()
        average_goal_conceded_home = home.GC.sum()/home.P.sum()
        home['HAR'] = (home.AGS)/average_goal_scored_home
        home['HDR'] = (home.AGC)/average_goal_conceded_home

        away_series = result_away
        away = pd.DataFrame(away_series, columns=[
                            'P', 'W', 'D', 'L', 'GS', 'GC'])

        away['GD'] = away.GS-away.GC
        away['PTS'] = (away.W*3)+away.D
        away['AGS'] = (away.GS)/away.P
        away['AGC'] = (away.GC)/away.P
        average_goal_scored_away = away.GS.sum()/away.P.sum()
        average_goal_conceded_away = away.GC.sum()/away.P.sum()
        away['AAR'] = (away.AGS)/average_goal_scored_away
        away['ADR'] = (away.AGC)/average_goal_conceded_away
        home_table = pd.concat([team, home], axis=1)
        away_table = pd.concat([team, away], axis=1)
        home_table = home_table.set_index('Team')
        home_table.sort_values(['PTS', 'GD'], ascending=False, inplace=True)
        away_table = away_table.set_index('Team')
        away_table.sort_values(['PTS', 'GD'], ascending=False, inplace=True)
        overall_table = pd.concat([home_table + away_table], axis=1)
        overall_table.sort_values(['PTS', 'GD'], ascending=False, inplace=True)


# calculating expected_goal

        for index, row in fixtures.iterrows():

            HAS = (home_table.HAR.loc[home_table.index == row['HomeTeam']]).tolist()[
                0]
            HDS = (home_table.HDR.loc[home_table.index == row['HomeTeam']]).tolist()[
                0]
            AAS = (away_table.AAR.loc[away_table.index == row['AwayTeam']]).tolist()[
                0]
            ADS = (away_table.ADR.loc[away_table.index == row['AwayTeam']]).tolist()[
                0]

            HEG = HAS*ADS
            AEG = AAS*HDS

# calculating team_performance
            HT = data.loc[data['HomeTeam'] == row['HomeTeam']]
            AT = data.loc[data['AwayTeam'] == row['AwayTeam']]
            HT = HT.tail()
            AT = AT.tail()

            try:
                f = HT.FTR.value_counts().H
            except:
                f = 0
            try:
                d = HT.FTR.value_counts().D
            except:
                d = 0

            try:
                f1 = AT.FTR.value_counts().A
            except:
                f1 = 0
            try:
                d1 = AT.FTR.value_counts().D
            except:
                d1 = 0
            HPR = round(((f*3 + d*1)/15)*100)
            APR = round(((f1*3 + d1*1)/15)*100)

    # calculate_probability(
            home_probs = (poisson.pmf(range(11), HEG))
            away_probs = (poisson.pmf(range(11), AEG))
            m = (np.outer(home_probs, away_probs))
            fixture = row['HomeTeam'] + "" + 'vs' + "" + row['AwayTeam']
            home_win = ((np.sum(np.tril(m, -1)))*100).round(2)
            draw = ((np.sum(np.diag(m)))*100).round(2)
            away_win = ((np.sum(np.triu(m, 1)))*100).round(2)
            date =row['Date']
            prediction = [date,country, fixture, home_win, draw, away_win, HPR, APR]
            predictions.append(prediction)

        df = pd.DataFrame(predictions, columns=[
            'Date','league', 'Teams', 'Homewin', 'Draw', 'Awaywin', 'Homeform', 'Awayform'])

        results =df.to_json(orient='records')
        parsed = json.loads(results)
        time.sleep(5)

        for result in parsed:
            data=[]
            obj, created = Prediction.objects.get_or_create(
                date=result['Date'],
                home_win=result['Homewin'],
                away_win=result['Awaywin'],
                draw =result['Draw'],
                league=result['league'],
                fixture=result['Teams'],
                home_form=result['Homeform'],
                away_form=result['Awayform'],
                )
            obj.save()
          

