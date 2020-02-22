import lambdaelo
import lambdabetlines
import requests
import random
import json
import os
from decimal import Decimal, ROUND_UP

# initialize a few env vars
accessToken = os.environ['groupme_access_key']
groupno = os.environ['group_num']

# sets the base API URL
base_url = "https://api.groupme.com/v3/groups/"

# sample elo list below:
"""
elo_list = [
            {
                'game_key': 'clipperspelicans',
                'away_team': {'team_name': 'clippers', 'win_prob': 53, 'abbreviated': ''}, 
                'home_team': {'team_name': 'pelicans', 'win_prob': 47, 'abbreviated': ''}
            }, 
            {
                'game_key': 'bucksnets', 
                'away_team': {'team_name': 'bucks', 'win_prob': 76, 'abbreviated': ''}, 
                'home_team': {'team_name': 'nets', 'win_prob': 24, 'abbreviated': ''}
            }, 
            {
                'game_key': 'sunsceltics', 
                'away_team': {'team_name': 'suns', 'win_prob': 16, 'abbreviated': ''}, 
                'home_team': {'team_name': 'celtics', 'win_prob': 84, 'abbreviated': ''}
            }
           ]
"""

def post_text(msg_text):
    # this module will make a post as the user whose token is provided.
    # it takes in the text that you want it to post and then this does
    # the backend API calls to actually post it

    # a GUID is required for all groupme messages. the code below
    # randomizes the GUID generation based on the typical format i've seen
    randGUID = 'botpost' + ''.join(random.choice('abcdef1234567890') for _ in range(25))

    # initializes some necessary components.
    # in the payload, you can also have attachments, lat/long, etc.
    endpoint = "/messages"
    headers = {"Content-Type": "application/json",
                "x-access-token": accessToken}
    payload = {"message": {"source_guid": randGUID, "text": msg_text}}

    # attempts to make the POST API calls. status code 200 is a success
    try:
        r = requests.post(base_url + groupno + endpoint,
                            data=json.dumps(payload),
                            headers=headers)
        return(r.status_code)
    except requests.exceptions.ConnectionError:
        print('Error')



def bet_win_exp(line):
    # this is our formula for determining the 538 numbers against
    if line < 0:
        bet_win_exp = Decimal(1 - (100 / (100 + abs(line))))
    else:
        bet_win_exp = Decimal(100 / (100 + line))

    # now we want to round the decimal up to the hundredths place
    bet_win_dec = Decimal(bet_win_exp.quantize(Decimal('.01'), rounding=ROUND_UP))
    # we'll put this in an integer since INT compare is easier than DEC
    bet_win_int = int(bet_win_dec * 100)

    return bet_win_int



def calculate_free_money(el, ll, stat_id):
    # the stat_id will either be home_team or away_team.
    # iterate through the lines until we get to Bovada
    for line in ll[stat_id]['lines']:
        if line['line_name'] == 'Bovada':
            # send to the function to calculate
            win_line = bet_win_exp(line['odds'])
            # now compare that value against the 538 metric
            if el[stat_id]['win_prob'] > win_line:
                # this is how we'll format the free money strings
                # BOS@UTAH: UTAH is -450. Odds = 82% win; ELO = 85% win
                # UTAH is -450. Odds = 82% win; ELO = 85% win
                # we'll format each of these respective numbers below
                free_money = '{0}@{1}: {2} is {3}. Odds = {4}% win; ELO = {5}% win'.format(
                                    ll['away_team']['abbreviated'],
                                    ll['home_team']['abbreviated'],
                                    ll[stat_id]['abbreviated'],
                                    "{0:+d}".format(line['odds']),
                                    win_line,
                                    el[stat_id]['win_prob'])
                return free_money
                

def make_free_money_string(elo_list, lines_list):
    # check to see if these lists exist
    if lines_list and elo_list:
        # make a little intro showing the number of games
        game_str = "Found {0} games on 538 and betting lines for {1} of those games.".format(
            len(elo_list), len(lines_list))
    else:
        # exit the module if there's no games
        final_str = "No games today, so no free money :/"
        return final_str

    # initialize the list
    free_money_list = []

    # we want to find matches on the game_key in both lists, so we 
    # will iterate through each until it matches
    for el in elo_list:
        for ll in lines_list:
            if el['game_key'] == ll['game_key']:
                # now that we've got a match, we want to see if there's
                # any free money opportunities. we send this off for a
                # calculation.
                free_money_list.append(calculate_free_money(el, ll, "away_team"))
                free_money_list.append(calculate_free_money(el, ll, "home_team"))

    # let's remove the None values from our free money list
    free_money_filtered = list(filter(None.__ne__, free_money_list))
    # print(free_money_filtered)

    # now we'll make a string for the free money counts.
    # we only want to do this if there are a non-zero amount of alerts
    if free_money_filtered:
        # identify # of free money alerts
        free_money_intro = "There are {0} free money alerts:".format(
                                        len(free_money_filtered))
        # take the list and make it into a string
        free_money_str = '\n'.join(str(p) for p in free_money_filtered)
        # take all the separate strings and put them together
        final_str = "{0}\n\n{1}\n{2}".format(
                        game_str,
                        free_money_intro,
                        free_money_str)

        return final_str
    else:
        # if we found games but no free money, then this is our message
        final_str = "{0}\n\nNo free money alerts today :/".format(
                        game_str)
        return final_str


def my_handler(event, context):
    # run the modules from the other files to get the base data
    elo_list = lambdaelo.main()
    lines_list = lambdabetlines.main()

    # get the string output for the message post
    bot_string = make_free_money_string(elo_list, lines_list)
    print(bot_string)

    # post it to groupme
    print(post_text(bot_string))
    print("posted to groupme")
