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
    pic_url = "https://i.groupme.com/" + rand_line

    return pic_url