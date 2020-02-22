## High Level Flow

* `lambdadriver.py` is the driver file
* Gets the data from 538 via `lambdaelo.py`
  * Uses the `html_table_parser.py` plug-in (courtesty of Josua Schmid) to grab some HTML elements
* Gets the betting line data via `lambdabetlines.py`
* Joins them back up in the driver file and posts the output to groupme
