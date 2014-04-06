import optparse
import urllib2
import time
import datetime

import pysolr


import ds
import fields
import traceback
import lweutils
import common_finance
import numpy


def simulate(options, args):
    stocks = common_finance.load_stocks(options.stocks_file)
    solr = pysolr.Solr(lweutils.SOLR_URL, timeout=10)
    simulate_stocks(solr, stocks)

def simulate_stocks(solr, stocks):
    print "Indexing Stocks"
    for symbol in stocks:
        vals = stocks[symbol]
        items = {"id": symbol, "symbol": symbol, "company": vals[1], "industry": vals[2], "city": vals[3],
                 "state": vals[4], "hierarchy": ["1/" + vals[2], "2/" + vals[4], "3/" + vals[3]]} # Start at 1/ for ease integration w/ JS
        common_finance.add(solr, [items], id, commit=False)
    pass


p = optparse.OptionParser()
p.add_option("-p", "--stocks_file", action="store", dest="stocks_file")
p.add_option("--historical_port", action="store", dest="historical_port", default="9898")
p.add_option("-x", "--index", action="store_true", dest="index") # Index the content
p.add_option("-s", "--sleep", action="store", dest="sleep")


opts, args = p.parse_args()

COLLECTION = opts.collection
LWS_URL = "http://" + opts.host + ":" + opts.api_port
API_URL = LWS_URL + "/api"
SOLR_URL = LWS_URL + "/solr/" + COLLECTION
COL_URL = API_URL + "/collections/" + COLLECTION
FIELDS_URL = COL_URL + '/fields'  #TODO: fix this
DS_URL = COL_URL + '/datasources'

opts.historical_solr = "http://" + opts.host + ":" + opts.historical_port + "/solr"
print "Hi Solr: "+ opts.historical_solr
if (opts.ui_host and opts.ui_port):
    lweutils.UI_URL = "http://" + opts.ui_host + ":" + opts.ui_port
else:
    lweutils.UI_URL = "http://" + opts.host + ":8989"
lweutils.UI_API_URL = lweutils.UI_URL + "/api"

simulate(opts, args)
