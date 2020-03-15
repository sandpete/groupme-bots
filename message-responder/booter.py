import requests
import os
import random

# initialize a few env vars
accessToken = os.environ['groupme_access_key']
groupno = os.environ['group_number']
# the boot mode is specific to this function. values are "self" and "random"
mode = os.environ['boot_mode']

# sets the API URL structure
base_url = "https://api.groupme.com/v3/groups/"



def get_member_json():
    headers = {"Content-Type": "application/json",
                "x-access-token": accessToken}

    # the URL we hit for the group member listing
    url = base_url + groupno

    # attempts to make the POST API calls
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        print('Error')

    # return the contents of the response
    content = r.json()

    return content

def get_self_id(content, user_id):
    """
    Map the requestor's user_id to their id. groupme has three different
    IDs so it's all very arcane
    """
    # iterate through members
    for member in content['response']['members']:
        # there's two things we need to check for:
        # 1 - if the user_id vals match
        # 2 - if the person is an admin
        if user_id == member['user_id']:
            if "user" in member["roles"]:
                chosen_id = member['id']
                return chosen_id
            # this condition happens when the IDs are a match but the person
            # is an admin. if that happens, we'll get a random ID instead
            else:
                chosen_id = get_random_id(content)
                return chosen_id
    


def get_random_id(content):
    """
    to get a random ID, you need to hit an endpoint, get the members, and
    then filter out the people that can't be booted (e.g., admins).
    """
    # initializes some necessary components.
    # there's no payload needed for a boot request
    
    # add the "good" IDs to a list (good meaning eligible for removal)
    good_ids = []
    # iterate through members
    for member in content['response']['members']:
        # the "user" flag means someone is eligible for booting
        if "user" in member["roles"]:
            # add the ID to the good list
            good_ids.append(member['id'])

    # now we just pick a random item from the good IDs
    chosen_id = random.choice(good_ids)

    return chosen_id


def boot_sequence(event):
    """
    ultimately, we want to remove someone from the group. i've built this
    so that you can toggle between a random person and the person who 
    asked for the boot sequence (a cruel twist of fate). this toggle is
    set at the environment variable level. the event is a json object
    passed through from the driver
    """
    json_content = get_member_json()

    if mode == "random":
        boot_id = get_random_id(json_content)
    elif mode == "self":
        self_user_id = event['user_id']
        boot_id = get_self_id(json_content, self_user_id)

    print("## CHOSEN BOOT ID")
    print(boot_id)

    # initializes some necessary components.
    # there's no payload needed for a boot request
    headers = {"Content-Type": "application/json",
                "x-access-token": accessToken}

    # the URL we hit for the removal is constructed as outlined below
    url = "{0}{1}{2}{3}{4}".format(
                                base_url,
                                groupno,
                                "/members/",
                                boot_id,
                                "/remove")
    print("## URL hit")
    print(url)

    # attempts to make the POST API calls
    try:
        r = requests.post(url, headers=headers)
        print("## STATUS CODE OF GROUPME API")
        print(r.status_code)
        return(r.status_code)
    except requests.exceptions.ConnectionError:
        print('Error')
