import os
import csv
import random

def photoboi():
    # we have an images csv file that contains all the image URLs.
    # this will open the file
    file_path = os.environ['LAMBDA_TASK_ROOT'] + "/images.csv"
    # file_path = "images.csv"
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
    pic_url = "https://i.groupme.com/" + line[0]

    return pic_url