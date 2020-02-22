# groupme-bots
A collection of bots that interact with the Groupme chat service. Each of these are running as a Python 3.7 AWS Lambda function. Keep in mind some of the API keys and other sensitive variables are stored as Lambda environment variables.

*To Do*
* Post more details about architecture
* Explain dependencies/upload zips (huge pain point in getting this to prod)

## Message Responder

Gets invoked each time a message is posted and posts a message back depending on the context.

## NBA Free Money

Checks arbitrage opportunities between betting lines and FiveThirtyEight ELO data. Runs once a day at a fixed time.
