import requests
import json


def get_crypto(input_text):
    # gets current prices of different cryptocurrencies

    # figure out which crypto we're looking up
    if "bitcoin" in input_text:
        symbol = "BTC"
    elif "bitcoin cash" in input_text:
        symbol = "BCH"
    elif "ethereum" in input_text:
        symbol = "ETH"
    elif "litecoin" in input_text:
        symbol = "LTC"
    elif "ripple" in input_text:
        symbol = "XRP"
    elif "tron" in input_text:
        symbol = "TRX"
    else:
        # combines the options into text. acts kind of like a help module
        msg = "I can give you the following crypto prices:\n"
        options = "bitcoin\nbitcoin cash\nethereum\nlitecoin\nripple\ntron"
        txt = msg + options
        return txt

    # API details to get the crypto details from
    crypto_url = "https://min-api.cryptocompare.com/data/price?fsym="
    currency = "&tsyms=USD"

    try:
        r = requests.get(crypto_url + symbol + currency)
        print(r.status_code)
    except requests.exceptions.ConnectionError:
        print('Error')

    # gets the JSON response
    content = r.json()
    price = content[u'USD']

    # putting it all together to make the final message
    msg = symbol + " is currently at $" + str(price)
    return msg