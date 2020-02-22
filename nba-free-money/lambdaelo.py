from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
from html_table_parser import HTMLTableParser

base_page = "https://projects.fivethirtyeight.com/2020-nba-predictions/games/"
elo_radio_button_id = "r2"


def initiate_driver():
    # set up some stuff for the browser configs
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
    chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"

    driver = webdriver.Chrome(options=chrome_options)

    return driver

def get_elo(driver):
    # the ELO info is only visible after clicking a radio button.
    # this will click the button and return the page info for parsing.
    radioElement = driver.find_element_by_id(elo_radio_button_id)
    radioElement.click()
    # wait for 5 seconds since some javascript will run
    time.sleep(5)

    return driver

def team_name_formatting(team):
    # does some string formatting to the team name
    team_frmt = team.replace(' ', '').lower()

    return team_frmt


def string_percent_to_integer(str_per):
    # converts something like "99%" to a float value
    try:
        dec = int(str_per.strip('%'))
    except:
        dec = -1
    return dec


def access_elements(driver, proj_type, matchup_list):
    # parses the HTML and gets us the elements we need

    # get today's games
    today_games = driver.find_element_by_css_selector('.day:nth-child(1)')
    # the parser is in a separate module; this will instantiate it
    p = HTMLTableParser()
    # the parser needs the raw HTML, not the webObjects
    p.feed(today_games.get_attribute('innerHTML'))
    # iterate through the table rows
    for matchup in p.tables:
        # each row will print in the following format:
        # [['', '7 p.m. Eastern', 'Elo spread', 'Win prob.', 'Score'], [''], ['', '', 'Nuggets', '', '40%', '', ''], ['', '', 'Pacers', '-2.5', '60%', '', ''], ['']]
        # each matchup has 5 rows; we care about rows 3 & 4.
        # within each row, the name and win probability are what we need
        away_team_long = team_name_formatting(matchup[2][2])
        away_team_win_prob = string_percent_to_integer(matchup[2][4])
        home_team_long = team_name_formatting(matchup[3][2])
        home_team_win_prob = string_percent_to_integer(matchup[3][4])
        
        game_dict = {
                        "game_key": away_team_long + home_team_long,
                        "away_team": {
                            "team_name": away_team_long,
                            "win_prob": away_team_win_prob
                        },
                        "home_team": {
                            "team_name": home_team_long,
                            "win_prob": home_team_win_prob
                        }
                    }
        # add each game to the tracking list
        matchup_list.append(game_dict)

    return matchup_list


def main():
    print("looking at 538...")
    # where we'll store each of the matchups
    matchup_list = []

    # get the headless web browser set up
    driver = initiate_driver()
    
    # open the web page
    page_data = ""
    driver.get(base_page)

    # click the radio button 
    elo_data = get_elo(driver)

    # parse the page data
    matchup_list = access_elements(elo_data, "elo", matchup_list)
    print("got 538 data")
    # close out the selenium driver
    driver.close()

    return matchup_list

# uncomment here if you want to run this by itself and see the output
# if __name__ == "__main__":
#     print(main())
