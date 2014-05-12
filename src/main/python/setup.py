import argparse
import urllib2
import time
import datetime

import pysolr
import common_finance

import datasource
import fields
import traceback
import logging
import sys

try:
    # Prefer lxml, if installed.
    from lxml import etree as ET
except ImportError:
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        raise ImportError("No suitable ElementTree implementation was found.")

import lweutils
from lweutils import sleep_secs


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

twitter_fields = {"batch_id": {"name": "batch_id"},
                  "body": {"name": "body"},
                  "Content-Encoding": {"name": "characterSet"},
                  "Content-Type": {"name": "mimeType"},
                  "createdAt": {"name": "dateCreated"},
                  "parsing": {"name": "parsing"},
                  "retweetCount": {"name": "retweetCount", "ft":"int"}, "source": {"name": "creator"},
                  "userId": {"name": "userId", "ft":"long"}, "content_length": {"name": "content_length", "ft":"int"},
                  "userLang": {"name": "lang"},
                  "userLocation": {"name": "userLocation", "ft":"text_en"},
                  "location": {"name": "location", "ft":"point"},
                  "userName": {"name": "author"},
                  "userScreenName": {"name": "userScreenName", "ft":"string"},
                  "isRetweet": {"name": "isRetweet", "ft":"boolean"},
                  "isRetweetedByMe": {"name": "isRetweetByMe", "ft":"boolean"},
                  "isFavorited": {"name": "isFavorited", "ft":"boolean"},
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


def command_setup(options):
    logger.debug("creating PySolr client for {}".format(SOLR_URL))
    solr = pysolr.Solr(SOLR_URL, timeout=10)
    logger.debug("created PySolr client")

    logger.debug("loading stocks from {}".format(options.stocks_file))
    stocks = common_finance.load_stocks(options.stocks_file)
    logger.debug("loaded {} stocks: {}".format(len(stocks), stocks))

    create_collection(options.finance_collection)
    create_collection(options.kibana_collection)

    if options.fields and options.create:
        create_fields(args)
    if options.twitter and options.create:
        create_twitter_ds(stocks, options.access_token, options.consumer_key, options.consumer_secret,
                          options.token_secret)
    if options.press and options.create:
        create_press_ds(stocks)
    historical_data_source = None
    company_datasource = None
    if options.external:
        historical_data_source = create_historical_ds(options)
        company_datasource = create_company_ds(options)
    if options.index:
        if company_datasource == None:
            company_datasource = datasource_connection.get(options.company_datasource_name)
        if company_datasource:
            print "Indexing for data source: " + company_datasource.datasource_id()
            company_solr = pysolr.Solr(options.company_solr_url, timeout=10)
            index_stocks(company_solr, stocks, company_datasource)
        else:
            print "Couldn't find datasource {}".format(options.company_datasource_name)

        if historical_data_source == None:
            historical_data_source = datasource_connection.get(options.historical_datasource_name)
        if historical_data_source:
            print "Indexing for data source: " + historical_data_source.datasource_id()
            historical_solr = pysolr.Solr(options.historical_solr_url, timeout=10)
            index_historical(historical_solr, stocks, historical_data_source, options.data_dir)
            solr.commit()
        else:
            print "Couldn't find datasource {}".format(options.historical_datasource_name)

def command_reindex(options):
    solr = pysolr.Solr(SOLR_URL, timeout=10)
    stocks = common_finance.load_stocks(options.stocks_file)
    historical_datasource = datasource_connection.get(options.historical_datasource_name)
    if (historical_datasource):
        logger.info("Reindexing for data source: " + historical_datasource.datasource_id())
        index_historical(solr, stocks, historical_datasource)
    else:
        print "Couldn't find datasource {}".format(options.company_datasource_name)

def command_delete(options):
    delete_datasources()
    delete_collections(options)

def command_help(options):
    p.print_help()

###############   

def delete_datasources():
    datasources = datasource_connection.datasources()
    logger.debug("datasources={}".format(datasources))
    for datasource in datasources.values():
        datasource.delete()

def delete_collections(options):
    my_collections = (options.finance_collection, options.kibana_collection)
    collections = [ c for c in list_collection_names() if c in my_collections ]
    for collection_name in collections:
        delete_collection(collection_name)

def index_stocks(solr, stocks, data_source):
    #Symbol,Company,City,State
    logger.info("Indexing Company Info")
    for symbol in stocks:
        vals = stocks[symbol]
        items = {"id": symbol, "symbol": symbol, "company": vals[1], "industry": vals[2], "city": vals[3],
                 "state": vals[4], "hierarchy": ["1/" + vals[2], "2/" + vals[4], "3/" + vals[3]]} # Start at 1/ for ease integration w/ JS
        common_finance.add(solr, [items], data_source.datasource_id(), commit=False)

def collection_exists(name):
    logger.info("checking for collection: " + name)
    rsp = lweutils.json_http(API_URL + "/collections", method='GET')
    logger.debug("collections: {}".format(rsp))
    for collection in rsp:
        if 'id' not in collection:
            logger.error("No id in collection")
        if collection['id'] == name:
            logger.debug("collection {} exists".format(name))
            return True
    return False

def create_collection(name):
    if collection_exists(name):
        logger.info("collection {} already exists".format(name))
    else:
        logger.info("Creating New Collection: {}".format(name))
        data = {"name": name}
        try:
            rsp = lweutils.json_http(API_URL + "/collections/" + name, method='PUT', data=data)
            logger.info("Created New Collection: {}".format(name))
            # otherwise enable_dynamic_schema will fail saying the schema is immutable
            sleep_secs(5, "waiting for collection to get created")
        except Exception as e:
            traceback.print_exc()

    enable_dynamic_schema(name)

def is_dynamic_schema_enabled(name):
    rsp = lweutils.json_http(API_URL + "/collections/{}/features".format(name))
    for feature in rsp:
        if feature['name'] == 'dynamicSchema':
            logger.debug("dynamicSchema={}".format(feature['name']))
            return feature['enabled']
    return False

def enable_dynamic_schema(name):
    if is_dynamic_schema_enabled(name):
        logger.info("dynamicSchema already enabled for collection {}".format(name))
    else:
        try:
            logger.info("Enabling dynamic schema for " + name)
            rsp = lweutils.json_http(API_URL + "/collections/{0}/features/dynamicSchema".format(name), method='PUT', data={'enabled':True})
            logger.info("Enabled dynamic schema for " + name)
            sleep_secs(5, "waiting for the dynamic schema to be enabled")
        except Exception as e:
            traceback.print_exc()

def delete_collection(name):
    logger.info("Deleting Collection: " + name)
    rsp = lweutils.json_http(API_URL + "/collections/" + name, method='DELETE')
    logger.debug("Deleted Collection: " + name)

def list_collection_names():
    rsp = lweutils.json_http(API_URL + "/collections/" , method='GET')
    collection_names = [ c['id'] for c in rsp ]
    logger.debug("collection names: {}".format(collection_names))
    return collection_names

def index_historical(solr, stocks, data_source, seriesDir):
    for symbol in stocks:
        logger.info("Indexing: " + symbol)
        #Get the data
        csv_path = seriesDir + "/" + symbol + ".csv"
        try:
            cached = open(csv_path)
            logger.debug("Found {} in the cache {}".format(symbol, csv_path))
            data = cached.read()
        except IOError:
            logger.debug("Could not find {} in the cache {}, so downloading".format(symbol, csv_path))
            year = datetime.date.today().year
            url="http://ichart.finance.yahoo.com/table.csv?s={}&f={}&ignore=.csv".format(symbol, year)
            response = urllib2.urlopen(url)
            data = response.read()
            output = open(csv_path, 'wb')
            output.write(data)
            output.close()
            sleep_secs(1, "so we don't get banned from yahoo")

        # parse the docs and send to solr
        lines = data.splitlines()
        lines.pop(0) # pop the first, as it is the list of columns
        for line in lines:
            #logger.debug(l: " + line)
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

            common_finance.add(solr, [items], data_source.datasource_id(), commit=False)
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
    url = "http://finance.yahoo.com/q/p?s={}+Press+Releases".format(stock)
    include_paths = [
        "http://finance\.yahoo\.com/news/.*",
        "http://finance\.yahoo\.com/q/p\?s={}+Press+Releases".format(stock)]
    name="PressRelease_" + stock
    datasource = datasource_connection.create_web(name=name, start_urls=url, depth=1, include_regexps=include_paths)
    #rsp = lweutils.json_http(DS_URL + "/datasources/" + id + "/job", method="PUT")
    datasource.start()
    return datasource

def create_press_ds(stocks):
    logger.info("Creating Crawler of Press Release data for all symbols")
    stock_lists = list(stocks)
    for stock in stock_lists:
        create_press_crawler(stock)

def create_twitter_ds(stocks, access_token, consumer_key, consumer_secret, token_secret):
    logger.info("Creating Twitter Data Source for all symbols")
    # can only do 400 tracks at a time
    stock_lists = list(stocks)
    length = len(stock_lists)
    if length > 0:
        steps = max(1, length / 100)
        step = 0
        logger.debug("steps={}, len={}".format(steps, length))
        for i in xrange(steps):
            section = stock_lists[step:step + 100]
            add_twitter(i, section, stocks, access_token, consumer_key, consumer_secret, token_secret)
            step += 101
        if step < length:
            section = stock_lists[step + 1:]
            add_twitter(i, section, stocks, access_token, consumer_key, consumer_secret, token_secret)


def add_twitter(i, stock_lists, stocks, access_token, consumer_key, consumer_secret, token_secret):
    logger.debug("add_twitter #{} {} {}".format(i, stock_lists, stocks))
    name="Twitter_{}".format(i)
    symbols = ""
    for symbol in stock_lists:
        symbols += "$" + symbol + ", " + stocks[symbol][1] + ", "
        #args.append("filter_track=$" + symbol)
        #args.append("filter_track=" + stocks[symbol][1])
    #args.append("filter_track=" + symbols[:len(symbols) - 1])
    # TODO: what is all that?

    datasource = datasource_connection.create_twitter(name=name, access_token=access_token, consumer_key=consumer_key,
        consumer_secret=consumer_secret, token_secret=token_secret)
    datasource.start()

def create_historical_ds(options):
    name="Historical"
    logger.info("Creating DS for {}".format(name))
    if datasource_connection.get(name) is not None:
        logger.debug("datasource {} already exists")
        return
    logger.debug("no existing datasource {}".format(name))

    #For 2.7, we will need to change the crawler type to push
    data = {"mapping": {"mappings": {"symbol": "symbol", "open": "open", "high": "high", "low": "low", "close": "close",
                     "trade_date":"trade_date",
                     "volume": "volume",
                     "adj_close": "adj_close"}}}
    datasource = datasource_connection.create_push(name=name, port=options.historical_port)
    #rsp = lweutils.json_http(COL_URL + "/datasources/" + id + "/mapping", method="PUT", data=data)
    datasource.start()
    return datasource

def create_company_ds(options):
    name="Company"
    logger.info("Creating DS for {}".format(name))
    if datasource_connection.get(name) is not None:
        logger.debug("datasource {} already exists")
        return
    logger.debug("no existing datasource {}".format(name))

    #For 2.7, we will need to change the crawler type to push
    mappings = {
        "mapping": {"mappings": {"symbol": "symbol", "company": "company", "industry": "industry", "city": "city",
                     "state": "state", "hierarchy": "hierarchy"}}}
    datasource = datasource_connection.create_push(name=name, port=options.company_port)
    #rsp = lweutils.json_http(COL_URL + "/datasources/" + id + "/mapping", method="PUT", data=data)
    datasource.start()
    return datasource

def create_banana_fields():
    fields.create(["name=user", "indexed=true", "stored=true", "type=string"], args.kibana_fields_url)
    fields.create(["name=group", "indexed=true", "stored=true", "type=string"], args.kibana_fields_url)
    #fields.create(["name=title", "indexed=true", "stored=true", "type=string"], args.kibana_fields_url)
    fields.create(["name=dashboard", "indexed=false", "stored=true", "type=string"], args.kibana_fields_url)

def create_fields(args):
    create_banana_fields()
    #Twitter
    print COLLECTION

    #Company info
    #Symbol,Company,Industry,City,State
    fields.create(["indexed=true", "stored=true", "name=RESULT_TYPE", "type=string"], FIELDS_URL)
    fields.update(["name=data_source_name", "copyFields=RESULT_TYPE", "type=string"], FIELDS_URL)
    fields.create(["indexed=true", "stored=true", "name=symbol", "type=string"], FIELDS_URL)

    fields.create(["indexed=true", "stored=true", "name=industry_facet", "type=string"], FIELDS_URL)
    fields.create(["indexed=true", "stored=true", "name=industry", "type=text_en", "copyFields=industry_facet"], FIELDS_URL)

    fields.create(["indexed=true", "stored=true", "name=company_facet", "type=string"], FIELDS_URL)
    fields.create(["indexed=true", "stored=true", "name=company", "type=text_en", "copyFields=company_facet"], FIELDS_URL)

    fields.create(["indexed=true", "stored=true", "name=city_facet", "type=string"], FIELDS_URL)
    fields.create(["indexed=true", "stored=true", "name=city", "type=text_en", "copyFields=city_facet"], FIELDS_URL)

    fields.create(["indexed=true", "stored=true", "name=hierarchy", "type=string", "multiValued=true"], FIELDS_URL)

    fields.create(["indexed=true", "stored=true", "name=state", "type=string"], FIELDS_URL)

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
    #create_field("price", "date")   # TODO: huh?

def create_field(field, type):
    fields.create(["indexed=true", "stored=true", "name=" + field + "_bucket", "type=string"], FIELDS_URL)
    fields.create(["indexed=true", "stored=true", "name=" + field, "type=" + type], FIELDS_URL)

#########################################

p = argparse.ArgumentParser(description='Setup Apollo Financial Demo.')

p.add_argument("--twitter", action='store_true',
    help="create the twitter datasource")
p.add_argument("--access_token", metavar="token", help="Twitter access token")
p.add_argument("--consumer_key", metavar="key", help="Twitter consumer key")
p.add_argument("--consumer_secret", metavar="secret", help="Twitter consumer secret")
p.add_argument("--token_secret", metavar="token", help="Twitter token secret")

p.add_argument("--data_dir", metavar="dir", default="../../../data",
    help="historical data directory (default: ../../../data)")

p.add_argument("--api_host", metavar="host", dest="host", default="localhost",
    help="Apollo backend API host (default: localhost)")
p.add_argument("--api_port", type=int, metavar="port", dest="api_port", default="8765",
    help="Apollo backend API port (default: 8765)")

p.add_argument("--ui_host", metavar="host", dest="ui_host", default="localhost",
    help="UI host (default: localhost)") # TODO: is this Apollo-admin or something else?
p.add_argument("--ui_port", type=int, metavar="port", dest="ui_port", default="8989",
    help="UI host (default: 8989)") # TODO: is this Apollo-admin or something else?

p.add_argument("--solr_host", metavar="host", dest="solr_host", default="localhost",
    help="Solr host (default: localhost)")
p.add_argument("--solr_port", type=int, metavar="port", dest="solr_port", default="8983",
    help="Solr port (default: 8983)")

p.add_argument("--connectors_host", metavar="host", default="localhost",
    help="Connectors host (default: localhost)")
p.add_argument("--connectors_port", type=int, metavar="port", dest="connectors_port", default="8984",
    help="Connectors port (default: 8984)")

p.add_argument("--external", action='store_true',
    help="create the external datasource")
p.add_argument("--fields", action='store_true',
    help="create the fields")

p.add_argument("--finance-collection", metavar="name", default="Finance",
    help="name of the financia collection (default: Finance)")
p.add_argument("--kibana-collection", metavar="name", default="kibana-int",
    help="name of the Kibana collection (default: kibana-int)")
p.add_argument("--company_datasource_name", metavar="name", default="Company",
    help="name of the company datasource (default: Company)")
p.add_argument("--historical_datasource_name", metavar="name", default="HistoricalPrices",
    help="name of the historical datasource (default: HistoricalPrices)")

p.add_argument("--create", action='store_true', dest="create",
    help="create collections and datasources")
p.add_argument("--action", action='append', dest="action", choices=['setup', 'delete', 'help'],
    help="the main action (default: setup)")

p.add_argument("--company_port", type=int, dest="company_port", default="9191",
    metavar="port",
    help="connectors solr update handler port for Company datasource")
p.add_argument("--historical_port", type=int, dest="historical_port", default="9898",
    help="connectors solr update handler port for History datasource",
    metavar="port")

p.add_argument("--stocks_file", type=file, metavar="file",
    default="../../../data/sp500List-30.txt",
    help="filename of the stocks file")

p.add_argument("--press", action='store_true', help="create press crawler")
p.add_argument("--index", action='store_true', help="index the content")

args = p.parse_args()

# TODO: FIX UP ALL THIS HACKY VARIABLE STUFF
COLLECTION = args.finance_collection
LWS_URL = "http://{}:{}/lucid".format(args.host, args.api_port)
API_URL = LWS_URL + "/api/v1"
SOLR_URL = "http://{}:{}/solr/{}".format(args.solr_host, args.solr_port, COLLECTION)
COL_URL = API_URL + "/collections/" + COLLECTION
FIELDS_URL = SOLR_URL + "/schema/fields"

CONNECTORS_URL = "http://{}:{}/connectors/api/v1/connectors".format(args.connectors_host, args.connectors_port)

args.kibana_fields_url = "http://{}:{}/solr/kibana-int/schema/fields".format(args.solr_host, args.solr_port)
args.company_solr_url = "http://{}:{}/solr".format(args.host, args.company_port)
args.historical_solr_url = "http://{}:{}/solr".format(args.host, args.historical_port)

lweutils.UI_URL = "http://{}:{}".format(args.ui_host, args.ui_port)
lweutils.UI_API_URL = lweutils.UI_URL + "/lucid/api/v1"

logger.debug("creating datasource connection {}".format(CONNECTORS_URL))
datasource_connection = datasource.DataSourceConnection(CONNECTORS_URL)
logger.debug("created datasource connection")

if args.action is None:
    args.action = ['setup']
for action in args.action:
    func = "command_" + action
    logger.debug("running {}".format(func))
    vars()[func](args)
