import optparse
import urllib2
import time

import pysolr

import ds
import fields

twitter_fields = {"batch_id": {"name": "batch_id"},
                  "body": {"name": "body"},
                  "Content-Encoding": {"name": "characterSet"},
                  "Content-Type": {"name": "mimeType"},
                  "createdAt": {"name": "dateCreated"},
                  "parsing": {"name": "parsing"},
                  "retweetCount": {"name": "retweetCount", "ft":"int", "facet":"true"}, "source": {"name": "creator"},
                  "userId": {"name": "userId", "ft":"long"}, "content_length": {"name": "content_length", "ft":"int"},
                  "userLang": {"name": "lang", "ft": "string", "facet":"true"},
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

from lweutils import SOLR_URL, COL_URL, API_URL, COLLECTION, json_http
########### top level actions

def setup(options, args):
    solr = pysolr.Solr(SOLR_URL, timeout=10)
    stocks = load_stocks(options.stocks_file)

    if options.collection:
        create_collection(COLLECTION)
    if options.fields:
        create_fields(args)
    if options.twitter:
        create_twitter_ds(stocks, options.access_token, options.consumer_key, options.consumer_secret,
                          options.token_secret)
    historicalDs = None
    companyDs = None
    if options.external:
        historicalDs = create_historical_ds()
        companyDs = create_company_ds()
    if options.index:
        if companyDs == None:
            companyDs = ds.get_id({"name": "Company"})
        if companyDs:
            index_stocks(solr, stocks, companyDs)
        else:
            print "Couldn't find Company DS"

        if historicalDs == None:
            historicalDs = ds.get_id({"name": "HistoricalPrices"})
            print "Id: " + str(historicalDs)
        if historicalDs:
            print "Indexing for data source: " + historicalDs
            index_historical(solr, stocks, historicalDs, options.data_dir)
            solr.commit()
        else:
            print "Couldn't find Data Source"



def reindex(options, args):
    solr = pysolr.Solr(SOLR_URL, timeout=10)
    stocks = load_stocks(options.stocks_file)
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
                 "state": vals[4]}
        add(solr, [items], id, commit=False)


def create_collection(name):
    data = {"name": name}
    rsp = json_http(API_URL + "/collections", method='POST', data=data)
    print "Created New Collection: " + data['name']
    #TODO: Add in Aggregate RequestHandler capability


def load_stocks(file):
    stocks = {}
    for line in open(file):
        if line.startswith("#") == False:
            vals = line.split(",")
            symbol = vals[0]
            stocks[symbol] = vals
    return stocks


def index_historical(solr, stocks, id, seriesDir):
    for symbol in stocks:
        print "Indexing: " + symbol
        #Get the data
        try:
            print "Found " + symbol + " in the cache"
            cached = open(seriesDir + "/" + symbol + ".csv")
            data = cached.read()
        except IOError:
            response = urllib2.urlopen(
                "http://ichart.finance.yahoo.com/table.csv?s=" + symbol + "&d=8&e=18&f=2013&g=d&a=8&b=7&c=1984&ignore=.csv")
            data = response.read();
            output = open(seriesDir + '/' + symbol + ".csv", 'wb')
            output.write(data)
            output.close()
            time.sleep(1) # sleep so we don't get banned

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

            add(solr, [items], id, commit=False)
            ## Date,Open,High,Low,Close,Volume,Adj Close
            #for r in csv.reader(data, lineterminator='\n'):
            #   print "r: " + str(len(r))
            #date,open_val,high,low,close,volume,adj_close = r
            #print date


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
    id = ds.create(args)
    data = create_twitter_mappings()
    rsp = json_http(COL_URL + "/datasources/" + id + "/mapping", method="PUT", data=data)
    rsp = json_http(COL_URL + "/datasources/" + id + "/job", method="PUT")


def create_historical_ds():
    print "Creating DS for Historical"
    id = ds.create(["name=HistoricalPrices", "type=external", "crawler=lucid.external",
                    "source=http://finance.yahoo.com/q/hp?s=SYMBOL+Historical+Prices", "source_type=Yahoo"])
    data = {
        "mappings": {"symbol": "symbol", "open": "open", "high": "high", "low": "low", "close": "close",
                     "volume": "volume",
                     "adj_close": "adj_close"}}
    rsp = json_http(COL_URL + "/datasources/" + id + "/mapping", method="PUT", data=data)
    return id


def create_company_ds():
    print "Creating DS for Company"
    id = ds.create(["name=Company", "type=external", "crawler=lucid.external", "source=CSV", "source_type=User"])
    data = {
        "mappings": {"symbol": "symbol", "company": "company", "industry": "industry", "city": "city",
                     "state": "state"}}
    rsp = json_http(COL_URL + "/datasources/" + id + "/mapping", method="PUT", data=data)
    return id


def create_fields(args):
    #Twitter
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


def create_field(field, type):
    fields.create(["indexed=true", "stored=true", "name=" + field + "_bucket", "field_type=string"])
    fields.create(["indexed=true", "stored=true", "name=" + field, "field_type=" + type, "include_in_results=true"])


def add(solr, docs, dsId, commit=True, boost=None, commitWithin=None, waitFlush=None, waitSearcher=None):
    """
    Adds or updates documents.
    Requires ``docs``, which is a list of dictionaries. Each key is the
    field name and each value is the value to index.
    Optionally accepts ``commit``. Default is ``True``.
    Optionally accepts ``boost``. Default is ``None``.
    Optionally accepts ``commitWithin``. Default is ``None``.
    Optionally accepts ``waitFlush``. Default is ``None``.
    Optionally accepts ``waitSearcher``. Default is ``None``.
    Usage::
        solr.add([
                            {
                                "id": "doc_1",
                                "title": "A test document",
                            },
                            {
                                "id": "doc_2",
                                "title": "The Banana: Tasty or Dangerous?",
                            },
                        ])
    """
    start_time = time.time()
    #self.log.debug("Starting to build add request...")
    message = ET.Element('add')

    if commitWithin:
        message.set('commitWithin', commitWithin)

    for doc in docs:
        message.append(solr._build_doc(doc, boost=boost))

    # This returns a bytestring. Ugh.
    m = ET.tostring(message, encoding='utf-8')
    # Convert back to Unicode please.
    m = pysolr.force_unicode(m)

    end_time = time.time()
    #self.log.debug("Built add request of %s docs in %0.2f seconds.", len(message), end_time - start_time)
    return update(solr, m, dsId, commit=commit, waitFlush=waitFlush, waitSearcher=waitSearcher)


def update(solr, message, dsId, clean_ctrl_chars=True, commit=True, waitFlush=None, waitSearcher=None):
    """
    Posts the given xml message to http://<self.url>/update and
    returns the result.

    Passing `sanitize` as False will prevent the message from being cleaned
    of control characters (default True). This is done by default because
    these characters would cause Solr to fail to parse the XML. Only pass
    False if you're positive your data is clean.
    """
    path = 'update/'

    # Per http://wiki.apache.org/solr/UpdateXmlMessages, we can append a
    # ``commit=true`` to the URL and have the commit happen without a
    # second request.
    query_vars = []

    if commit is not None:
        query_vars.append('commit=%s' % str(bool(commit)).lower())

    if waitFlush is not None:
        query_vars.append('waitFlush=%s' % str(bool(waitFlush)).lower())

    if waitSearcher is not None:
        query_vars.append('waitSearcher=%s' % str(bool(waitSearcher)).lower())
    if dsId is not None:
        query_vars.append("lucidworks_fields=true")
        query_vars.append("fm.ds=" + dsId)
    if query_vars:
        path = '%s?%s' % (path, '&'.join(query_vars))

    # Clean the message of ctrl characters.
    if clean_ctrl_chars:
        message = pysolr.sanitize(message)

    return solr._send_request('post', path, message, {'Content-type': 'text/xml; charset=utf-8'})


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
p.add_option("-l", "--collection", action="store", dest="collection") #create the collection
p.add_option("-n", "--action", action="store", dest="action")
p.add_option("-o", "--velocity_dest", action="store", dest="velocity_dest") # Create the Twitter DS
p.add_option("--api_port", action="store", dest="api_port", default="8888")
p.add_option("--ui_port", action="store", dest="ui_port", default="8989")
p.add_option("-p", "--stocks_file", action="store", dest="stocks_file")
p.add_option("-s", "--consumer_secret", action="store", dest="consumer_secret")
p.add_option("-t", "--token_secret", action="store", dest="token_secret")
p.add_option("-v", "--velocity_src", action="store", dest="velocity_src") # Create the Twitter DS
p.add_option("-w", "--twitter_ds", action="store_true", dest="twitter") # Create the Twitter DS
p.add_option("-x", "--index", action="store_true", dest="index") # Index the content

opts, args = p.parse_args()
action = opts.action
COLLECTION = opts.collection
LWS_URL = "http://" + opts.host + ":" + opts.api_port
API_URL = LWS_URL + "/api"
SOLR_URL = LWS_URL + "/solr/" + COLLECTION
COL_URL = API_URL + "/collections/" + COLLECTION

if (opts.ui_host and opts.ui_port):
    UI_URL = "http://" + opts.ui_host + ":" + opts.ui_port
else:
    UI_URL = "http://" + opts.host + ":8989"
UI_API_URL = UI_URL + "/api"

if opts.all:
    opts.external = True
    opts.fields = True
    opts.twitter = True
    opts.index = True

if action in ACTIONS:
    ACTIONS[action](opts, args)
else:
    raise Exception(action + " is not a valid action")

