Apollo Financial Demo
=====================

Simple Financial Demo for Apollo that indexes S&amp;P 500 company info,
historical stock prices and Twitter feeds. The data is loaded into Apollo
with [Python](https://www.python.org) scripts.

The demo includes a trading dashboard application based on
[LucidWorks SiLK](http://www.lucidworks.com/lucidworks-silk/),
which is based on [Banana](https://github.com/LucidWorks/banana), a Solr port of Kibana 3.

# Pre-requisites

## For the data loading script

* Python (I used 2.7.6)
* Python json lib (`pip install json`)
* Python ldap lib (`pip install python-ldap`). You will need gcc installed for this
* Python httplib2 (`pip install httplib2`)
* Pysolr (`pip install pysolr`)
* LucidWorks Apollo and its system requirements (Java 7)
* Twitter API authorization (see
[lucidworks docs](http://docs.lucidworks.com/display/lweug/Twitter+Stream+Data+Sources) and
[Twitter's developer documentation](http://dev.twitter.com)
 * You will need your API key, API Secret, Access token, Access token secret

## For the dashboard application

* [Node.js](http://nodejs.org). (`brew install node`)
* project dependencies (`npm install`)


### Caveats

Only tested on OS X, against Apollo on Linux.

Getting Started
=================

Install Apollo, and run its solr, apollo and connectors in separate windows:

    cd /opt/lucidworks/apollo
    ./bin/run-solr.sh
    ./bin/run.sh
    ./bin/run-connectors.sh

Clone this project:

    git clone --branch apollo git@github.com:LucidWorks/lws-financial-demo.git

Load the data (adjust the APOLLO_HOST and Twitter details for your environment):

    cd src/main/python
    APOLLO_HOST=192.168.0.106
    python setup.py \
      --access_token="$TWITTER_ACCESS_TOKEN" \
      --consumer_key="$TWITTER_CONSUMER_KEY" \
      --consumer_secret="$TWITTER_CONSUMER_SECRET" \
      --token_secret="$TWITTER_ACCESS_TOKEN_SECRET" \
      --stocks_file=../../../data/sp500List-30.txt \
      --data_dir=../../../data \
      --api_host=$APOLLO_HOST \
      --ui_host=$APOLLO_HOST \
      --ui_port=8181 \
      --solr_host=$APOLLO_HOST \
      --connectors_host=$APOLLO_HOST \
      --create --external --fields \
      --index --press --twitter

(appear to no longer be valid: `--ui_host=$APOLLO_HOST \` and `--ui_port=8181 \`)

This will setup collections, fields and data for the companies listed in the file `sp500List-30.txt`

Modify the `server.js` file in the main directory to point to your Apollo host.  The default is:

    var baseUrl = "http://localhost:8983/solr";

Do One-Time Setup:

    npm install   # only needed once

If you see the warning `npm WARN package.json LucidWorksFinanceDemo@0.0.1 No repository field.` this can [be ignored] [1].

Start the dashboard:
   
    node server.js

Point your browser to [http://localhost:3334/#/dashboard](http://localhost:3334/#/dashboard)

Things to Try
=============

In the dashboard, hover over the color wheel at the bottom right, showing the stock symbol.
Click on a stock, note how that produces an extra "terms:must" box at the top right, and note
how the graphs update accordingly.

In Solr, do searches for:

    data_source_s:company
    data_source_s:historical
    data_source_s:Twitter_0
    data_Source_s:PressRelease_AAPL

In Apollo, point a browser at (replace IP address with your Apollo host):

    http://192.168.0.106:8984/connectors/api/v1/index-pipelines
    http://192.168.0.106:8984/connectors/api/v1/index-pipelines/historical
    http://192.168.0.106:8984/connectors/api/v1/connectors/datasources/
    http://192.168.0.106:8984/connectors/api/v1/connectors/datasources/PressRelease_AAPL


Developing
==========

If you're working on the python code, run the above command with `--action=delete`
to destroy all collections, datasources and pipelines, so that you can run the script
again with a clean slate.
IMPORTANT: this will destroy ALL datasources, even those not added by this script.

You can use `../../../data/sp500List-1.txt` to load a single stock (Apple).


[1]: http://stackoverflow.com/questions/16827858/npm-warn-package-json
