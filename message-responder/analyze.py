import requests
import random
import json
import os
import csv
import re

# initialize a few env vars
key = os.environ['vision_api_key']



def analyzer(input_attachment, msg_text):
    # this will take the input_attachment value (which could be null)
    # and the message text. it will use the attachment URL first, but
    # if that's blank it'll extract a URL from the message. Once it
    # gets a valid URL, it'll send it to another module for processing

    # initialize a success variable to say whether it found it or not
    success = False 

    # only want to pass input_attachment if it's not null
    if input_attachment != 'null':
        output = input_attachment
        success = True
    # need to run the regex to make sure the message contains
    # a valid URL to run against
    else:
        url_regex = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(msg_text))
        # need to make sure there's not an empty set of results
        if len(url_regex) > 0:
            # findall returns a list; only want the first hit
            output = url_regex[0]
            success = True
        # no hits found anywhere in the msg
        else:
            output = "no valid URL found"

    print(output)
    return output, success


def visionAPI(url):

    # URL and key are separated for ease. Key is obtained from
    # https://console.cloud.google.com/apis/credentials?project=groupmeimagetag
    base = "https://vision.googleapis.com/v1/images:annotate?key="

    # making a POST request to the Vision API endpoint. body is JSON.
    payload = {
      "requests": [
        {
          "features": [
            {
              "type": "LABEL_DETECTION",
              "maxResults": 5
            },
            {
              "type": "LOGO_DETECTION",
              "maxResults": 2
            },
            {
              "type": "FACE_DETECTION"
            },
            {
              "type": "SAFE_SEARCH_DETECTION"
            },
            {
              "type": "WEB_DETECTION"
            }
          ],
          "image": {
            "source": {
              "imageUri": url
            }
          }
        }
      ]
    }

    # attempts to make the POST API calls. status code 200 is a success
    try:
        r = requests.post(base + key,
            data=json.dumps(payload))
        print(r.status_code)
        print(r.text)
    except requests.exceptions.ConnectionError:
        print('Error')

    # gets the JSON response
    content = r.json()

    return content


def parse_vision_JSON(content):
    # there should only be 1 response so we set the index after [responses]
    # to zero. This will separate each label
    response_root = content['responses'][0]

    # there are four things we're after: labels, logos, faces and safesearch.
    # we'll use a try and except to catch KeyErrors, meaning that the item
    # isn't present in the JSON. that's okay - the vision API will only
    # return items it finds. If there's no key error, we'll iterate through
    # each of the elements and add them to a list.

    # initialize lists. the first three are straightforward; the faces
    # could have more than one face
    best_guess_list = []
    web_list = []
    label_list = []
    safesearch_list = []
    logo_list = []
    faces_list = []

    # labels
    try:
        for label in response_root['labelAnnotations']:
            # grabs the description value
            label_desc = label.get('description', 'null')
            # if the description isn't null, add it to the list
            if label_desc != 'null':
                label_list.append(label_desc)
    except KeyError:
        pass

    # web detection
    try:
        for web_entity in response_root['webDetection']['webEntities']:
            # grabs the description value
            web_desc = web_entity.get('description', 'null')
            # if the description isn't null, add it to the list
            if web_desc != 'null':
                web_list.append(web_desc)

        if len(web_list) > 5:
            web_list = web_list[:5]
    except KeyError:
        pass

    # web best guess detection
    try:
        for best_guess in response_root['webDetection']['bestGuessLabels']:
            # grabs the description value
            guess_label = best_guess.get('label', 'null')
            # if the description isn't null, add it to the list
            if guess_label != 'null':
                best_guess_list.append(guess_label)

        if len(best_guess_list) > 3:
            best_guess_list = best_guess_list[:3]
    except KeyError:
        pass

    # added two lists
    # safesearch elements
    try:
        safesearch_root = response_root['safeSearchAnnotation']
        # there are five total elements, but we only want three
        adult = safesearch_root['adult']
        violence = safesearch_root['violence']
        racy = safesearch_root['racy']

        # add the elements to the list
        safesearch_list.append(adult)
        safesearch_list.append(violence)
        safesearch_list.append(racy)
            
    except KeyError:
        pass

    # logos
    try:
        for logo in response_root['logoAnnotations']:
            # grabs the description value
            logo_desc = logo.get('description', 'null')
            # if the description isn't null, add it to the list
            if logo_desc != 'null':
                logo_list.append(logo_desc)
    except KeyError:
        pass

    # iterates through the faces
    try:
        for face in response_root['faceAnnotations']:
            # grabs the relevant face values
            joy = face.get('joyLikelihood')
            sorrow = face.get('sorrowLikelihood')
            anger = face.get('angerLikelihood')
            surprise = face.get('surpriseLikelihood')

            # adds each of the values to the list
            faces_list.append(joy)
            faces_list.append(sorrow)
            faces_list.append(anger)
            faces_list.append(surprise)

        # to avoid exceeding the message post length, we only want
        # three faces. if the length of the list is greater than 12,
        # we'll strip off some elements. (3 faces, 4 elements)
        if len(faces_list) > 12:
            faces_list = faces_list[:12]

    except KeyError:
        pass

    return best_guess_list, web_list, label_list, safesearch_list, logo_list, faces_list


def vision_list_handler(best_guess_list, web_list, label_list,
    safesearch_list, logo_list, faces_list):
    # the vision API has been separated into lists. we'll take those
    # lists and make it ready to print.

    # initializes a list for containing all text values.
    text_all = []

    # formats the best guess list for printing
    if best_guess_list:
        # separates each list element with a comma
        best_guess_list = ', '.join(map(str, best_guess_list))
        guess_text = "My Best Guess\n" + best_guess_list
        # add this to the master list
        text_all.append(guess_text)

    # formats the web list for printing
    if web_list:
        # separates each list element with a comma
        web_list = ', '.join(map(str, web_list))
        web_text = "Similar Image Labels\n" + web_list
        # add this to the master list
        text_all.append(web_text)


    # formats the label list for printing
    if label_list:
        # separates each list element with a comma
        label_list = ', '.join(map(str, label_list))
        label_text = "Image Labels\n" + label_list
        # add this to the master list
        text_all.append(label_text)

    # formats the faces list for printing. this is the most complex.
    if faces_list:
        # these will be in groups of four
        # i will only be a max of 2 (3 faces; i is from 0 to 2)
        # we want different lists depending on which face number is chosen.
        # this sets the face groupings for the list elements

        # initializing a list of face text values
        face_text_list = []

        for i in range(0, len(faces_list)/4):
            if i == 0:
                # face 1
                faces_list_cut = faces_list[:4]
            elif i == 1:
                # face 2
                faces_list_cut = faces_list[4:8]
            elif i == 2:
                # face 3
                faces_list_cut = faces_list[8:12]

            # each face needs an intro with a value that isn't in the list
            face_intro = "*Face {}* - ".format(i+1)
            # attach the list elements to the text below
            face_text_body = "Joy: {}, Sorrow: {}, Anger: {}, Surprise: {}".format(*faces_list_cut)
            # combine these two together 
            face_text = face_intro + face_text_body
            # append this combined value into the list of face_text vals
            face_text_list.append(face_text)

        # separates each list element with a new line
        face_text_list = '\n'.join(map(str, face_text_list))
        face_text_final = "Facial Analysis\n" + face_text_list
        # add this to the master list
        text_all.append(face_text_final)

    # formats the logo list for printing
    if logo_list:
        # separates each list element with a comma
        logo_list = ', '.join(map(str, logo_list))
        logo_text = "Image Logos\n" + logo_list
        # add this to the master list
        text_all.append(logo_text)


    if safesearch_list:
        safesearch_text = "Content Evaluation\nAdult: {}, Violence: {}, Racy: {}".format(*safesearch_list)
        # add this to the master list
        text_all.append(safesearch_text)

    text_concat = '\n\n'.join(text_all)

    return text_concat