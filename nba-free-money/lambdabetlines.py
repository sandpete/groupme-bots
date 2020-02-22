import json
from datetime import datetime
import requests
import os

# the API key for the bets API is stored as a lambda env. var
bet_api_key = os.environ['bet_api_key']


def team_name_formatting(team):
    # does some string formatting to the team name
    # this is also the same in elo.py - make changes there too
    team_frmt = team.replace(' ', '').lower()

    return team_frmt


# this is only for testing purposes. the API call is for prod
def open_json():
    with open("lines.json") as json_file:
        # parse the file as json
        data = json.load(json_file)

    return data

def make_api_call():
    # get today's date since that's part of the API call
    today = datetime.today().strftime('%Y-%m-%d')
    # API URL details
    url = "https://therundown-therundown-v1.p.rapidapi.com/sports/4/events/" + today
    querystring = {"offset":"240"}
    headers = {
        'x-rapidapi-host': "therundown-therundown-v1.p.rapidapi.com",
        'x-rapidapi-key': bet_api_key
        }
    # make the call and return any errors
    r = requests.get(url, headers=headers, params=querystring)
    r.raise_for_status()
    # load it as json
    content = r.json()

    return content


def parse_line_data(json_obj, line_val):
    # try to grab the components from this particular line.
    # return nothing if it's not available
    try:
        away_odds = json_obj['lines'][line_val]["moneyline"]["moneyline_away"]
        home_odds = json_obj['lines'][line_val]["moneyline"]["moneyline_home"]
        line_name = json_obj['lines'][line_val]["affiliate"]["affiliate_name"]
        # piece it all together into two dicts - one for home team, one for away
        home_line = {
                            "odds": home_odds,
                            "line_name": line_name
                        }

        away_line = {
                            "odds": away_odds,
                            "line_name": line_name
                        }
    # utilizes some error handling in case it can't find the element
    except (KeyError, ValueError):
        home_line = None
        away_line = None
    # returns the home & away lines
    return away_line, home_line



def main():
    # uncomment the open_json module if you're testing
    # lines_data = open_json()
    print("making betting API call")
    lines_data = make_api_call()

    # initialize list
    lines_list = []
    print("got betting data")
    # this will parse each game into the elements we need
    for event in lines_data['events']:
        # initialize the lists
        away_lines = []
        home_lines = []
        # team data - just basic parsing & slight formatting
        away_team_long = team_name_formatting(event['teams_normalized'][0]['mascot'])
        away_team_abbr = event['teams_normalized'][0]['abbreviation']
        home_team_long = team_name_formatting(event['teams_normalized'][1]['mascot'])
        home_team_abbr = event['teams_normalized'][1]['abbreviation']

        # the API uses affiliate IDs for the oddsmakers:
        # 12 = bodog, 2 = bovada, 1 = 5dimes
        # call a function to get the right elements and then add to master
        away_line, home_line = parse_line_data(event, "2")
        away_lines.append(away_line)
        home_lines.append(home_line)
        away_line, home_line = parse_line_data(event, "12")
        away_lines.append(away_line)
        home_lines.append(home_line)
        away_line, home_line = parse_line_data(event, "1")
        away_lines.append(away_line)
        home_lines.append(home_line)

        # put this in the format we need it in
        line_dict = {
                        "game_key": away_team_long + home_team_long,
                        "away_team": {
                            "abbreviated": away_team_abbr,
                            "lines": away_lines
                        },
                        "home_team": {
                            "abbreviated": home_team_abbr,
                            "lines": home_lines
                        }
                    }
        # append this to the overall list
        lines_list.append(line_dict)

    # print(lines_list)
    return lines_list