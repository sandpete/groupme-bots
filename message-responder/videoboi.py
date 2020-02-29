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
        row_count = sum(1 for line in reader)
        # picks a random number between 0 and the row_count.
        # this is how we select the image to obtain.
        rand_val = random.randint(0, row_count)

    # i kept getting errors trying to read the same file, so we'll close
    # it out and open it again
    with open(file_path) as csvfile:
        # turns the CSV into a list
        data=list(csv.reader(csvfile))
        # grab the random line value
        rand_line = data[rand_val][0]

    # add the full URL
    video_url = video_url_format + rand_line

    return video_url