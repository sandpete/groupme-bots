## High Level Flow

* `botpost.py` is the driver file
* Gets invoked from the API Gateway hooks
* Parses the message text
* Identifies whether it needs to execute a function
  * `stonks.py` - creates a chart of the six-month price performance
  * `photoboi.py` - posts a random image from the group's history (looks at the `images.csv` file - limited info loaded to github)
  * `crypto.py` - posts the price of certain coins
  * `news.py` - posts news headlines from various sources
  * `analyze.py` - takes an input image and runs it through facial/object recognition and posts the results (can be used with `photoboi`)
