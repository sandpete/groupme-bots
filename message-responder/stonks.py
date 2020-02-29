import pygal
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
import requests
import json
import os
import re
from datetime import date
from datetime import datetime

# get lambda env var
api_key = os.environ['stock_api_key']


def stonks(ticker):
    # static variables for all
    alpha_vantage_endpoint = "https://www.alphavantage.co/query?"
    # specific to the daily time series function
    stock_daily_history_function = "TIME_SERIES_DAILY"
    # JSON output variables
    day_header = "Time Series (Daily)"
    close_header = "4. close"
    # we have to save an image file; here's the path to it
    stock_svg = "/tmp/stonk.svg"
    stock_png = "/tmp/stonk.png"

    # put everything together into the API endpoint
    stock_daily_history_api = "{0}function={1}&symbol={2}&apikey={3}".format(
                                                alpha_vantage_endpoint,
                                                stock_daily_history_function,
                                                ticker,
                                                api_key)

    try:
        # make the API call
        r = requests.get(stock_daily_history_api)
        # error out if there's not a 200 status response
        r.raise_for_status()
    except:
        pass

    # load the response as JSON
    content = r.json()
    # any errors will show up with a 
    if "Error Message" in content:
        # gets the JSON response
        print("Error - not a valid ticker")
    else:
        # initialize the x and y axis lists of values
        values = []
        date_axis = []
        # iterate through the days available
        for day in content[day_header]:
            # convert the string dates to datetime objects
            date_val = datetime.strptime(day, "%Y-%m-%d")
            # gets the close price for each day as a float value
            price = float(content[day_header][day][close_header])
            # create a list for each date & price combo
            value = (date_val, price)
            # creates a list of dictionaries of the following format:
            # ({'value': (2019-01-01, 123.24)}, {'value': ...})
            # this format plays nicely with the chart format that will follow
            values.append({'value': value})

        # grabs the min/max values for price & dates
        min_price = min(item['value'][1] for item in values)
        max_price = max(item['value'][1] for item in values)
        min_date = min(item['value'][0] for item in values)
        max_date = max(item['value'][0] for item in values)

        # formats text into the title of the chart
        title_txt = "${0} between {1} and {2}".format(
                                ticker,
                                datetime.strftime(min_date, "%Y-%m-%d"),
                                datetime.strftime(max_date, "%Y-%m-%d"))

        # this uses the pygal module to create a line chart.
        # the x axis is the date value and the y axis is the stock price
        xy_chart = pygal.DateTimeLine(
            x_label_rotation=35, 
            show_legend=False,
            title=title_txt,
            show_dots=False,
            x_title="Date",
            y_title="Price (in $)",
            x_value_formatter=lambda dt: dt.strftime("%m/%d"),
            show_y_guides=False,
            show_x_guides=False
            )
            
        # here we add the values from the list of dicts we created
        xy_chart.add('series name', values)
        # render the SVG to a file
        xy_chart.render_to_file(stock_svg)
        # read the SVG file into a Drawing object
        drawing = svg2rlg(stock_svg)
        # convert the Drawing object to a PNG
        renderPM.drawToFile(drawing, stock_png)
        # post this image to groupme's image service
        img_url = post_image(stock_png)
        # make the post to the group chat with the image embedded.
        # the function returns a status code so it'll print the number
        print(post_img_attachment(img_url))



def get_stock(msg_text):
    # makes a regex match on the first stock it sees
    # does not work for multiple tickers
    input_txt = re.findall(r'[$][A-Za-z][\S]*', str(msg_text))
    # strip out punctuation
    stock_tick = re.sub(r'[^\w\s]','',input_txt)
    
    # make sure it's not an empty result
    if len(stock_tick) > 0:
        # findall returns a list
        first_hit = stock_tick[0]
        # strips out the first character (i.e., the dollar sign)
        stock_strip = first_hit[1:]
        # makes it upper case
        ticker = stock_strip.upper()
        # send to the processing function
        stonks(ticker)
