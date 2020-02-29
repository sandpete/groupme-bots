import os
import csv
import random


def videoboi():
    # we have a videos csv file that contains all the video URLs.
    # this will open the file
    file_path = os.environ['LAMBDA_TASK_ROOT'] + "/videos.csv"
    # we need the group number to get the URL for the videos
    groupno = os.environ['group_number']
    # initialize the URL format of the videos
    video_url_format = "https://v.groupme.com/{0}/".format(groupno)
    # file_path = "videos.csv"
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile)
        # get row count
        row_count = sum(1 for line in f)
        # picks a random number between 0 and the row_count.
        # this is how we select the image to obtain.
        rand_val = random.randint(0, row_count)

        # grab the value from the random row value
        line = next((x for i, x in enumerate(reader) if i == rand_val), None)

    # add the full URL
    pic_url = video_url_format + line[0]

    return video_url
