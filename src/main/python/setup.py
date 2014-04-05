import optparse
import urllib2
import time
import datetime

import pysolr
import common_finance

import ds
import fields
import traceback

twitter_fields = {"batch_id": {"name": "batch_id"},
                  "body": {"name": "body"},
                  "Content-Encoding": {"name": "characterSet"},
                  "Content-Type": {"name": "mimeType"},
                  "createdAt": {"name": "dateCreated"},
                  "parsing": {"name": "parsing"},
                  "retweetCount": {"name": "retweetCount", "ft":"int", "facet":"true"}, "source": {"name": "creator"},
                  "userId": {"name": "userId", "ft":"long"}, "content_length": {"name": "content_length", "ft":"int"},
                  "userLang": {"name": "lang"},
                  "userLocation": {"name": "userLocation", "ft":"text_en"},
                  "location": {"name": "location", "ft":"point"},
                  "userName": {"name": "author"},
                  "userScreenName": {"name": "userScreenName", "ft":"string"},
                  "isRetweet": {"name": "isRetweet", "ft":"boolean", "facet":"true"},
                  "isRetweetedByMe": {"name": "isRetweetByMe", "ft":"boolean", "facet":"true"},
                  "isFavorited": {"name": "isFavorited", "ft":"boolean", "facet":"true"},
                  "isPossiblySensitive": {"name": "isPossiblySensitive", "ft":"boolean"},
                  "isTruncated": {"name": "isTruncated", "ft":"boolean"},
                  "inReplyToStatusId": {"name": "inReplyToStatusId", "ft":"long"},
                  "inReplyToScreenName": {"name": "inReplyToScreenName", "ft":"text_en"},
                  "inReplyToUserId": {"name": "inReplyToUserId", "ft":"long"},
                  "contributor": {"name": "contributor", "ft":"long"}, "placeFullName": {"name": "placeFullName", "ft":"text_en"},
                  "placeCountry": {"name": "placeCountry", "ft":"text_en"},
                  "placeAddress": {"name": "placeAddress", "ft":"text_en"}, "placeType": {"name": "placeType", "ft":"text_en"},
                  "placeURL": {"name": "placeUrl", "ft":"string"},
                  "placeId": {"name": "placeId", "ft":"string"}, "placeName": {"name": "placeName", "ft":"text_en"},
                  "userMentionName": {"name": "userMentionName", "ft":"text_en"},
                  "userMentionScreenName": {"name": "userMentionScreenName", "ft":"text_en"},
                  "userMentionStart": {"name": "userMentionStart", "ft":"int"},
                  "userMentionEnd": {"name": "userMentionEnd", "ft":"int"}, "url": {"name": "url"},
                  "urlExpanded": {"name": "urlExpanded", "ft":"string"},
                  "urlDisplay": {"name": "urlDisplay", "ft":"string"}, "tags": {"name": "keywords"},
                  "tagStart": {"name": "tagStart", "ft":"int"}, "tagEnd": {"name": "tagEnd", "ft":"int"},
                  "mediaId": {"name": "mediaId", "ft":"long"}, "mediaUrl": {"name": "mediaUrl", "ft":"string"}}
try:
    # Prefer lxml, if installed.
    from lxml import etree as ET
except ImportError:
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        raise ImportError("No suitable ElementTree implementation was found.")

import lweutils
########### top level actions




def setup(options, args):
    solr = pysolr.Solr(lweutils.SOLR_URL, timeout=10)
    stocks = common_finance.load_stocks(options.stocks_file)

    if options.collection and options.create:
        create_collection(lweutils.COLLECTION)
        create_collection("kibana-int")
    if options.fields and options.create:
        create_fields(args)
    if options.twitter and options.create:
        create_twitter_ds(stocks, options.access_token, options.consumer_key, options.consumer_secret,
                          options.token_secret)
    if options.press and options.create:
        create_press_ds(stocks)
    historicalDs = None
    companyDs = None
    if options.external:
        historicalDs = create_historical_ds(options.historical_port)
        companyDs = create_company_ds(options.company_port)
    if options.index:
        if companyDs == None:
            companyDs = ds.get_id({"name": "Company"})
        if companyDs:
            company_solr = pysolr.Solr(options.company_solr, timeout=10)
            time.sleep(5)
            index_stocks(company_solr, stocks, companyDs)
        else:
            print "Couldn't find Company DS"

        if historicalDs == None:
            historicalDs = ds.get_id({"name": "HistoricalPrices"})
            print "Id: " + str(historicalDs)
        if historicalDs:
            print "Indexing for data source: " + historicalDs
            historical_solr = pysolr.Solr(options.historical_solr, timeout=10)
            time.sleep(5)
            index_historical(historical_solr, stocks, historicalDs, options.data_dir)
            solr.commit()
        else:
            print "Couldn't find Data Source"




def reindex(options, args):
    solr = pysolr.Solr(lweutils.SOLR_URL, timeout=10)
    stocks = common_finance.load_stocks(options.stocks_file)
    id = ds.get_id({"name": "HistoricalPrices"})
    if (id):
        print "Reindexing for data source: " + id
        index_historical(solr, stocks, id)
    else:
        print "Couldn't find Data Source"

###############   

def index_stocks(solr, stocks, id):
    #Symbol,Company,City,State
    print "Indexing Company Info"
    for symbol in stocks:
        vals = stocks[symbol]
        items = {"id": symbol, "symbol": symbol, "company": vals[1], "industry": vals[2], "city": vals[3],
                 "state": vals[4], "hierarchy": ["1/" + vals[2], "2/" + vals[4], "3/" + vals[3]]} # Start at 1/ for ease integration w/ JS
        common_finance.add(solr, [items], id, commit=False)



def create_collection(name):
    data = {"name": name}
    try:
        print "Trying: " + name
        rsp = lweutils.json_http(lweutils.API_URL + "/collections", method='POST', data=data)
        print "Created New Collection: " + data['name']
    except Exception as e:
        traceback.print_exc()
    #TODO: Add in Aggregate RequestHandler capability




def index_historical(solr, stocks, id, seriesDir):
    for symbol in stocks:
        print "Indexing: " + symbol
        #Get the data
        try:
            cached = open(seriesDir + "/" + symbol + ".csv")
            print "Found " + symbol + " in the cache"
            data = cached.read()
        except IOError:
            print "Downloading " + symbol
            year = datetime.date.today().year
            response = urllib2.urlopen(
                "http://ichart.finance.yahoo.com/table.csv?s=" + symbol + "&f=" + str(year) + "&ignore=.csv")
            data = response.read()
            output = open(seriesDir + '/' + symbol + ".csv", 'wb')
            output.write(data)
            output.close()
            time.sleep(1)  # sleep so we don't get banned

        # parse the docs and send to solr
        lines = data.splitlines()
        lines.pop(0) # pop the first, as it is the list of columns
        for line in lines:
            #print "l: " + line
            items = {}
            date, open_val, high, low, close, volume, adj_close = line.split(",")
            items["id"] = symbol + date
            items["symbol"] = symbol
            items["trade_date"] = date + "T00:00:00Z"
            items["open"] = open_val
            items["high"] = high
            items["low"] = low
            items["close"] = close
            items["volume"] = volume
            items["adj_close"] = adj_close
            # TODO
            # Precompute buckets into the ranges for the buckets

            common_finance.add(solr, [items], id, commit=False)
            ## Date,Open,High,Low,Close,Volume,Adj Close
            #for r in csv.reader(data, lineterminator='\n'):
            #   print "r: " + str(len(r))
            #date,open_val,high,low,close,volume,adj_close = r
            #print date


def create_press_crawler(stock):
    #data = {"mapping": {"mappings": {"symbol": "symbol", "open": "open", "high": "high", "low": "low", "close": "close",
    #                 "trade_date":"trade_date",
    #                 "volume": "volume",
    #                 "adj_close": "adj_close"}}}
    url = "http://finance.yahoo.com/q/p?s=" + stock + "+Press+Releases"
    include_paths = ["http://finance\.yahoo\.com/news/.*", "http://finance\.yahoo\.com/q/p\?s=" + stock + "+Press+Releases"]
    id = ds.create(["name=PressRelease_" + stock, "type=web",
                    "bounds=none",
                    "url=" + url,
                    "crawler=lucid.aperture", "crawl_depth=2", "include_paths=" + include_paths[0],
                    "include_paths=" + include_paths[1]])
    rsp = lweutils.json_http(lweutils.COL_URL + "/datasources/" + id + "/job", method="PUT")
    return id


def create_press_ds(stocks):
    print "Creating Crawler of Press Release data for all symbols"
    stock_lists = list(stocks)
    for stock in stock_lists:
        create_press_crawler(stock)



def create_twitter_ds(stocks, access_token, consumer_key, consumer_secret, token_secret):
    print "Creating Twitter Data Source for all symbols"
    # can only do 400 tracks at a time
    stock_lists = list(stocks)
    length = len(stock_lists)
    if length > 0:
        steps = max(1, length / 100)
        step = 0
        print "The steps: " + str(steps) + " len: " + str(length)
        for i in xrange(steps):
            section = stock_lists[step:step + 100]
            add_twitter(i, section, stocks, access_token, consumer_key, consumer_secret, token_secret)
            step += 101
        if step < length:
            section = stock_lists[step + 1:]
            add_twitter(i, section, stocks, access_token, consumer_key, consumer_secret, token_secret)


def add_twitter(i, stock_lists, stocks, access_token, consumer_key, consumer_secret, token_secret):
    args = ["name=Twitter_" + str(i), "access_token=" + access_token, "consumer_key=" + consumer_key,
            "consumer_secret=" + consumer_secret,
            "token_secret=" + token_secret, "type=twitter_stream", "crawler=lucid.twitter.stream", "sleep=10000"]
    print stock_lists
    symbols = ""
    for symbol in stock_lists:
        symbols += "$" + symbol + ", " + stocks[symbol][1] + ", "
        #args.append("filter_track=$" + symbol)
        #args.append("filter_track=" + stocks[symbol][1])
    args.append("filter_track=" + symbols[:len(symbols) - 1])
    data = {"mapping":create_twitter_mappings()}
    id = ds.create(args, data)
    #rsp = lweutils.json_http(lweutils.COL_URL + "/datasources/" + id + "/mapping", method="PUT", data=data)
    rsp = lweutils.json_http(lweutils.COL_URL + "/datasources/" + id + "/job", method="PUT")


def create_historical_ds(historical_port=9898):
    print "Creating DS for Historical"
    #For 2.7, we will need to change the crawler type to push
    data = {"mapping": {"mappings": {"symbol": "symbol", "open": "open", "high": "high", "low": "low", "close": "close",
                     "trade_date":"trade_date",
                     "volume": "volume",
                     "adj_close": "adj_close"}}}
    id = ds.create(["name=HistoricalPrices", "type=push", "crawler=lucid.push", "port=" + historical_port], data)
        #           "source=http://finance.yahoo.com/q/hp?s=SYMBOL+Historical+Prices"
        #, "source_type=Yahoo"

    #rsp = lweutils.json_http(lweutils.COL_URL + "/datasources/" + id + "/mapping", method="PUT", data=data)
    return id


def create_company_ds(company_port=9191):
    print "Creating DS for Company"
    #For 2.7, we will need to change the crawler type to push
    mappings = {
        "mapping": {"mappings": {"symbol": "symbol", "company": "company", "industry": "industry", "city": "city",
                     "state": "state", "hierarchy": "hierarchy"}}}
    id = ds.create(["name=Company", "type=push", "crawler=lucid.push", "port=" + company_port], mappings)
     #"source=CSV", "source_type=User"])
    #rsp = lweutils.json_http(lweutils.COL_URL + "/datasources/" + id + "/mapping", method="PUT", data=data)
    return id


def create_fields(args):
    #Twitter
    print lweutils.COLLECTION
    for field in twitter_fields:
        if twitter_fields[field] and 'ft' in twitter_fields[field]:
            facet = "false"
            if 'facet' in twitter_fields[field]:
                facet="true"

            fields.create(["indexed=true", "stored=true", "name=" + twitter_fields[field]['name'], "field_type=" + twitter_fields[field]['ft'], "facet=" + facet, "include_in_results=true"])

    #Company info
    #Symbol,Company,Industry,City,State
    fields.create(["indexed=true", "stored=true", "name=RESULT_TYPE", "field_type=string", "include_in_results=true"])
    fields.update(["name=data_source_name", "copy_fields=RESULT_TYPE"])
    fields.create(
        ["indexed=true", "stored=true", "name=symbol", "field_type=string", "facet=true", "include_in_results=true"])

    fields.create(["indexed=true", "stored=true", "name=industry_facet", "field_type=string", "facet=true"])
    fields.create(["indexed=true", "stored=true", "name=industry", "field_type=text_en", "copy_fields=industry_facet",
                   "include_in_results=true"])

    fields.create(["indexed=true", "stored=true", "name=company_facet", "field_type=string", "facet=true"])
    fields.create(["indexed=true", "stored=true", "name=company", "field_type=text_en", "copy_fields=company_facet",
                   "include_in_results=true"])

    fields.create(["indexed=true", "stored=true", "name=city_facet", "field_type=string", "facet=true"])
    fields.create(["indexed=true", "stored=true", "name=city", "field_type=text_en", "copy_fields=city_facet",
                   "include_in_results=true"])

    fields.create(["indexed=true", "stored=true", "name=hierarchy", "field_type=string", "include_in_results=true",
                   "multi_valued=true"])

    fields.create(
        ["indexed=true", "stored=true", "name=state", "field_type=string", "facet=true", "include_in_results=true"])



    #Historical
    create_field("open", "float")
    create_field("trade_date", "date")
    create_field("high", "float")
    create_field("low", "float")
    create_field("close", "float")
    create_field("volume", "long")
    create_field("adj_close", "float")

    #Intra Day
    create_field("quote_date", "date")
    create_field("price", "date")


def create_field(field, type):
    fields.create(["indexed=true", "stored=true", "name=" + field + "_bucket", "field_type=string"])
    fields.create(["indexed=true", "stored=true", "name=" + field, "field_type=" + type, "include_in_results=true"])




def create_twitter_mappings():
    print "Creating Twitter Field Mappings"
    mappings = {}
    for field in twitter_fields:
        mappings[field] = twitter_fields[field]['name']
    return {"mappings": mappings}

    ##
def help(solr, options, args):
        """display the list of commands"""
        print """Usage: setup.py {cmd} [k1=v1 k2=v2 ...]
 Commands...
  help     => prints this help
  setup    => Setup all the fields and import all the data
  add      => Add a new Ticker symbol
"""

ACTIONS = {
        'help': help,
        'setup': setup,
    }

#########################################


p = optparse.OptionParser()
p.add_option("-a", "--access_token", action="store", dest="access_token")
p.add_option("-A", "--all", action="store_true", dest="all")
p.add_option("-c", "--consumer_key", action="store", dest="consumer_key")
p.add_option("-d", "--data_dir", action="store", dest="data_dir")
p.add_option("-e", "--external_ds", action="store_true", dest="external") # create the external ds

p.add_option("-f", "--fields", action="store_true", dest="fields") # add the fields
p.add_option("--api_host", action="store", dest="host", default="localhost")
p.add_option("--ui_host", action="store", dest="ui_host", default="localhost")
p.add_option("-l", "--collection", action="store", dest="collection") #name the collection
p.add_option("--create", action="store", dest="create") #create things like collection, etc.

p.add_option("-n", "--action", action="store", dest="action")
p.add_option("-o", "--velocity_dest", action="store", dest="velocity_dest") # Create the Twitter DS
p.add_option("--api_port", action="store", dest="api_port", default="8888")
p.add_option("--ui_port", action="store", dest="ui_port", default="8989")
p.add_option("--company_port", action="store", dest="company_port", default="9191")
p.add_option("--historical_port", action="store", dest="historical_port", default="9898")
p.add_option("-p", "--stocks_file", action="store", dest="stocks_file")
p.add_option("-s", "--consumer_secret", action="store", dest="consumer_secret")
p.add_option("-t", "--token_secret", action="store", dest="token_secret")
p.add_option("-v", "--velocity_src", action="store", dest="velocity_src") # Create the Twitter DS
p.add_option("-w", "--twitter_ds", action="store_true", dest="twitter") # Create the Twitter DS
p.add_option("-r", "--press", action="store_true", dest="press") #
p.add_option("-x", "--index", action="store_true", dest="index") # Index the content

opts, args = p.parse_args()
action = opts.action
# TODO: FIX UP ALL THIS HACKY VARIABLE STUFF
lweutils.COLLECTION = opts.collection
lweutils.LWS_URL = "http://" + opts.host + ":" + opts.api_port
lweutils.API_URL = lweutils.LWS_URL + "/api"
lweutils.SOLR_URL = lweutils.LWS_URL + "/solr/" + lweutils.COLLECTION
lweutils.COL_URL = lweutils.API_URL + "/collections/" + lweutils.COLLECTION
fields.FIELDS_URL = lweutils.COL_URL + '/fields'  #TODO: fix this
ds.DS_URL = lweutils.COL_URL + '/datasources'
opts.company_solr = "http://" + opts.host + ":" + opts.company_port + "/solr"
opts.historical_solr = "http://" + opts.host + ":" + opts.historical_port + "/solr"
print "Co Solr: " + opts.company_solr
print "Hi Solr: "+ opts.historical_solr

if (opts.ui_host and opts.ui_port):
    lweutils.UI_URL = "http://" + opts.ui_host + ":" + opts.ui_port
else:
    lweutils.UI_URL = "http://" + opts.host + ":8989"
lweutils.UI_API_URL = lweutils.UI_URL + "/api"

if opts.all:
    opts.external = True
    opts.fields = True
    opts.twitter = True
    opts.index = True
    opts.press = True
    opts.create = True

if action in ACTIONS:
    ACTIONS[action](opts, args)
else:
    raise Exception(action + " is not a valid action")

