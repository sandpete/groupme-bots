import requests
import json
import os

# get lambda env var
api_key = os.environ['news_api_key']

def get_news(input_text):
    # this will return the top news stories for a given source

    # figure out which source we want to use
    if "espn" in input_text:
        source = "espn"
    elif "bbc" in input_text:
        source = "bbc-news"
    elif "bloomberg" in input_text:
        source = "bloomberg"
    elif "buzzfeed" in input_text:
        source = "buzzfeed"
    elif "cnn" in input_text:
        source = "cnn"
    elif "crypto" in input_text:
        source = "crypto-coins-news"
    elif "fox" in input_text:
        source = "fox-news"
    elif "nfl" in input_text:
        source = "nfl-news"
    elif "reddit" in input_text:
        source = "reddit-r-all"
    elif "nyt" in input_text:
        source = "the-new-york-times"
    elif "wsj" in input_text:
        source = "the-wall-street-journal"
    elif "wapo" in input_text:
        source = "the-washington-post"
    else:
        source = "google-news"

    # URL endpoints for the API. we will establish source below
    news_url = "https://newsapi.org/v2/top-headlines?sources="
    param = "&apiKey="

    try:
        r = requests.get(news_url + source + param + api_key)
        print(r.status_code)
    except requests.exceptions.ConnectionError:
        print('Error')

    # gets the JSON response
    content = r.json()
    articles = content[u'articles']
    # setting it to return only the top 5 articles
    top_articles = articles[:5]
    headline_text = "Here are the headlines for " + source + ":"

    # for reach article, it will get the title and add it to the list
    for article in top_articles:
        headline = article[u'title']
        # adds newlines plus the headline
        headline_text += "\n\n" + headline

    return headline_text