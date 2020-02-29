import requests
import random
import json
import os
import re
import photoboi
import news
import crypto
import stonks
import analyze
import videoboi

# initialize a few env vars
accessToken = os.environ['groupme_access_key']
groupno = os.environ['group_number']

# sets the base API URL
base_url = "https://api.groupme.com/v3/groups/"



def post_img_attachment(img_url):
    # this module will make a post as the user whose token is provided.
    # it takes in the text that you want it to post and then this does
    # the backend API calls to actually post it

    # a GUID is required for all groupme messages. the code below
    # randomizes the GUID generation based on the typical format i've seen
    randGUID = 'botpost' + ''.join(random.choice('abcdef1234567890') for _ in range(25))

    # initializes some necessary components.
    # puts the image URL we got from the upload into the attachment
    # of our new post
    endpoint = "/messages"
    headers = {"Content-Type": "application/json",
                "x-access-token": accessToken}
    payload = {"message": {"source_guid": randGUID, 
                            "text": "capitalism rules",
                            "attachments":[{"type":"image",
                                            "url":img_url}]}}

    # attempts to make the POST API calls. status code 200 is a success
    try:
        r = requests.post(base_url + groupno + endpoint,
                            data=json.dumps(payload),
                            headers=headers)
        return(r.status_code)
    except requests.exceptions.ConnectionError:
        print('Error')



def post_image(img_fpath):
    # endpoint for API call
    pic_service_url = "https://image.groupme.com/pictures"
    # loads in the stock PNG image
    data = open(img_fpath, 'rb').read()
    # makes the API call to groupme for the image post.
    # POSTs the image data
    r = requests.post(url=pic_service_url,
                        data=data,
                        headers={'Content-Type': 'image/jpeg',
                                 'X-Access-Token': accessToken})
    # exit if any errors arise
    r.raise_for_status()
    print(r.status_code)
    # return the URL of the image we just posted
    content = r.json()
    return content["payload"]["url"]
    

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

def my_handler(event, context):
    
    # checks each message posted in the group to see if it contains
    # the name of the bot. if it does, it will then do a few more
    # string comparisons to know which function to call
    
    # check that it's not posted by itself to avoid infinite loops
    if "botpost" not in event['source_guid']:
    # if event['sender_id'] != "45530059":
        
        # putting the input text to lowercase for better matches
        input_text = event['text'].lower()

        # handle attachment URLs for images
        # the value will default to 'null' if a URL attachment is not found
        # true JSON path to what we want: [event][attachments][url]
        if event['attachments']:
            for url in event['attachments']:
                input_attachment = url.get('url', 'null')
        else:
            input_attachment = 'null'

        # vision & photoboi combo handler
        if ("@photo" in input_text) and ("@analyze" in input_text):
            # gets the image URL
            url_val = photoboi.photoboi()
            # passes the value to the vision API & gets back JSON
            json_content = analyze.visionAPI(url_val)
            # parses the JSON into a usable format
            list_a, list_b, list_c, list_d, list_e, list_f = analyze.parse_vision_JSON(json_content)
            # formats the message text into a block of text
            msg_val = analyze.vision_list_handler(list_a, list_b, list_c, list_d, list_e, list_f)
            # concatenate the pic URL and the vision text
            url_plus_vision_text = url_val + "\n\n" + msg_val
            post_text(url_plus_vision_text)
        # photoboi handler
        elif "@photo" in input_text:
            # gets the image URL and posts it
            pic_url = photoboi.photoboi()
            post_text(pic_url)
        # analyze handler
        elif "@analyze" in input_text:
            # send both vals bc the pic could be either place
            url_val, success = analyze.analyzer(input_attachment, input_text)
            # if it found a valid URL, proceed
            if success == True:
                json_content = analyze.visionAPI(url_val)
                list_a, list_b, list_c, list_d, list_e, list_f = analyze.parse_vision_JSON(json_content)
                msg_val = analyze.vision_list_handler(list_a, list_b, list_c, list_d, list_e, list_f)
                post_text(msg_val)
            else:
                post_text(url_val)
        # videoboi handler
        elif "@video" in input_text:
            # gets the video URL and posts it
            vid_url = videoboi.videoboi()
            post_text(vid_url)
        # odds handler
        elif "@odds" in input_text:
            # generate random number and post it
            rand_num = random.randint(0, 100)
            post_text(str(rand_num) + "%")
        elif "@crypto" in input_text:
            crypto_price = crypto.get_crypto(input_text)
            post_text(crypto_price)
        elif "@news" in input_text:
            news = news.get_news(input_text)
            post_text(news)
        elif "@help" in input_text:
            intro = "I recognize the following:\n"
            options = """@photo will grab a random photo from the history
                        \n@video will grab a random vid from the history
                        \n@analyze (attach pic or paste URL)
                        \n@odds
                        \n@crypto (+ help for more info) along with the coin name
                        \n@news
                        \n$[stock_name]
                        \n@help"""
            msg = intro + options
            post_text(msg)
        elif "$" in input_text:
            # create a local file with the PNG chart
            local_img_path = stonks.get_stock(input_text)
            # send the file to the groupme image upload service
            img_url = post_image(local_img_path)
            # post the message to the chat and print the status code
            print(post_img_attachment(img_url))
        elif "@bot" in input_text:
            post_text("use @help to see what I do")

