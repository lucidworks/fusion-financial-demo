import argparse
import httplib2
import urllib2
import time
import datetime

import pysolr
import common_finance

import datasource
# import ds
import fields
import traceback
import logging
import sys
import os
import re

try:
    # Prefer lxml, if installed.
    from lxml import etree as ET
except ImportError:
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        raise ImportError('No suitable ElementTree implementation was found.')

import lweutils
from lweutils import sleep_secs


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

twitter_fields = {'batch_id': {'name': 'batch_id'},
                  'body': {'name': 'body'},
                  'Content-Encoding': {'name': 'characterSet'},
                  'Content-Type': {'name': 'mimeType'},
                  'createdAt': {'name': 'dateCreated'},
                  'parsing': {'name': 'parsing'},
                  'retweetCount': {'name': 'retweetCount', 'ft': 'int'}, 'source': {'name': 'creator'},
                  'userId': {'name': 'userId', 'ft': 'long'}, 'content_length': {'name': 'content_length', 'ft': 'int'},
                  'userLang': {'name': 'lang'},
                  'userLocation': {'name': 'userLocation', 'ft': 'text_en'},
                  'location': {'name': 'location', 'ft': 'point'},
                  'userName': {'name': 'author'},
                  'userScreenName': {'name': 'userScreenName', 'ft': 'string'},
                  'isRetweet': {'name': 'isRetweet', 'ft': 'boolean'},
                  'isRetweetedByMe': {'name': 'isRetweetByMe', 'ft': 'boolean'},
                  'isFavorited': {'name': 'isFavorited', 'ft': 'boolean'},
                  'isPossiblySensitive': {'name': 'isPossiblySensitive', 'ft': 'boolean'},
                  'isTruncated': {'name': 'isTruncated', 'ft': 'boolean'},
                  'inReplyToStatusId': {'name': 'inReplyToStatusId', 'ft': 'long'},
                  'inReplyToScreenName': {'name': 'inReplyToScreenName', 'ft': 'text_en'},
                  'inReplyToUserId': {'name': 'inReplyToUserId', 'ft': 'long'},
                  'contributor': {'name': 'contributor', 'ft': 'long'},
                  'placeFullName': {'name': 'placeFullName', 'ft': 'text_en'},
                  'placeCountry': {'name': 'placeCountry', 'ft': 'text_en'},
                  'placeAddress': {'name': 'placeAddress', 'ft': 'text_en'},
                  'placeType': {'name': 'placeType', 'ft': 'text_en'},
                  'placeURL': {'name': 'placeUrl', 'ft': 'string'},
                  'placeId': {'name': 'placeId', 'ft': 'string'}, 'placeName': {'name': 'placeName', 'ft': 'text_en'},
                  'userMentionName': {'name': 'userMentionName', 'ft': 'text_en'},
                  'userMentionScreenName': {'name': 'userMentionScreenName', 'ft': 'text_en'},
                  'userMentionStart': {'name': 'userMentionStart', 'ft': 'int'},
                  'userMentionEnd': {'name': 'userMentionEnd', 'ft': 'int'}, 'url': {'name': 'url'},
                  'urlExpanded': {'name': 'urlExpanded', 'ft': 'string'},
                  'urlDisplay': {'name': 'urlDisplay', 'ft': 'string'}, 'tags': {'name': 'keywords'},
                  'tagStart': {'name': 'tagStart', 'ft': 'int'}, 'tagEnd': {'name': 'tagEnd', 'ft': 'int'},
                  'mediaId': {'name': 'mediaId', 'ft': 'long'}, 'mediaUrl': {'name': 'mediaUrl', 'ft': 'string'}}


def command_setup(options):
    logger.debug('creating PySolr client for {}'.format(SOLR_URL))
    solr = pysolr.Solr(SOLR_URL, timeout=10)
    logger.debug('created PySolr client')

    logger.debug('loading stocks from {}'.format(options.stocks_file))
    stocks = common_finance.load_stocks(options.stocks_file)
    logger.debug('loaded {} stocks: {}'.format(len(stocks), stocks))

    create_collection(options.finance_collection)
    create_collection(options.kibana_collection)

    if options.fields and options.create:
        create_fields(args)
    if options.twitter and options.create:
        create_twitter_ds(stocks, options.finance_collection, options.access_token, options.consumer_key, options.consumer_secret,
                          options.token_secret)
    if options.press and options.create:
        create_press_ds(options, stocks)
    historical_data_source = None
    company_datasource = None
    if options.external:
        historical_data_source = create_historical_ds(options)
        company_datasource = create_company_ds(options)
    if options.index:
        if company_datasource == None:
            company_datasource = datasource_connection.get(
                options.company_datasource_name)
        if company_datasource:
            logger.info('Indexing for data source {}'.format(
                company_datasource.datasource_id()))
            company_solr = pysolr.Solr(options.company_solr_url, timeout=10)
            index_stocks(company_solr, stocks, company_datasource)
        else:
            logger.error(
                "Couldn't find datasource {}".format(options.company_datasource_name))

        if historical_data_source == None:
            historical_data_source = datasource_connection.get(
                options.historical_datasource_name)
        if historical_data_source:
            logger.info('Indexing for data source {}'.format(
                historical_data_source.datasource_id()))
            historical_solr = pysolr.Solr(
                options.historical_solr_url, timeout=10)
            index_historical(
                historical_solr, stocks, historical_data_source, options.data_dir)
        else:
            logger.error("Couldn't find datasource {}".format(
                options.historical_datasource_name))
        solr.commit()


def command_reindex(options):
    solr = pysolr.Solr(SOLR_URL, timeout=10)
    stocks = common_finance.load_stocks(options.stocks_file)
    historical_datasource = datasource_connection.get(
        options.historical_datasource_name)
    if (historical_datasource):
        logger.info(
            'Reindexing for data source: ' + historical_datasource.datasource_id())
        index_historical(solr, stocks, historical_datasource)
    else:
        logger.error(
            "Couldn't find datasource {}".format(options.company_datasource_name))


def command_delete(options):
    delete_datasources()
    delete_jobs()
    delete_collections(options)
    delete_pipelines(options)


def command_help(options):
    p.print_help()

###############


def delete_datasources():
    datasources = datasource_connection.datasources()
    logger.debug('datasources={}'.format(datasources))
    for datasource in datasources.values():
        datasource.delete()


def delete_collections(options):
    my_collections = (options.finance_collection, options.kibana_collection)
    collections = [c for c in list_collection_names() if c in my_collections]
    for collection_name in collections:
        delete_collection(collection_name)


def delete_pipelines(options):
    pipelines = lweutils.json_http(PIPELINE_URL)
    for pipeline in pipelines:
        # TODO: get this from somewhere
        if pipeline['id'] in ['company', 'historical', 'twitter']:
            lweutils.json_http(
                PIPELINE_URL + '/' + pipeline['id'], method='DELETE')


def index_stocks(solr, stocks, data_source):
    # Symbol,Company,City,State
    logger.info('Indexing Company Info')
    for symbol in stocks:
        vals = stocks[symbol]
        try:
            items = {'id': symbol, 'symbol': symbol, 'company': vals[1], 'industry': vals[2], 'city': vals[3],
                     'state': vals[4], 'hierarchy': ['1/' + vals[2], '2/' + vals[4], '3/' + vals[3]]}  # Start at 1/ for ease integration w/ JS
        except Exception as e:
            logger.error(
                'Error while parsing stock {} with values {}'.format(symbol, vals))
            traceback.print_exc()

        common_finance.add(
            solr, [items], data_source.datasource_id(), commit=False)


def collection_exists(name):
    logger.info('checking for collection: ' + name)
    rsp = lweutils.json_http(API_URL + '/collections', method='GET')
    logger.debug('collections: {}'.format(rsp))
    for collection in rsp:
        if 'id' not in collection:
            logger.error('No id in collection')
        if collection['id'] == name:
            logger.debug('collection {} exists'.format(name))
            return True
    return False


def create_collection(name):
    if collection_exists(name):
        logger.info('collection {} already exists'.format(name))
    else:
        logger.info('Creating New Collection: {}'.format(name))
        data = {'name': name}
        try:
            rsp = lweutils.json_http(
                API_URL + '/collections/' + name, method='PUT', data=data)
            logger.info('Created New Collection: {}'.format(name))
            # otherwise enable_dynamic_schema will fail saying the schema is
            # immutable
            sleep_secs(5, 'waiting for collection to get created')
        except Exception as e:
            traceback.print_exc()

    enable_feature(name, 'dynamicSchema')
    enable_feature(name, 'signals')


def is_feature_enabled(coll_name, feature_name):
    rsp = lweutils.json_http(
        API_URL + '/collections/{}/features'.format(coll_name))
    for feature in rsp:
        if feature['name'] == feature_name:
            logger.debug('{}={}'.format(feature_name, feature['name']))
            return feature['enabled']
    return False


def enable_feature(name, feature_name):
    if is_feature_enabled(name, feature_name):
        logger.info(
            '{} already enabled for collection {}'.format(feature_name, name))
    else:
        try:
            logger.info('Enabling ' + feature_name + ' for ' + name)
            rsp = lweutils.json_http(API_URL + '/collections/{0}/features/{1}'.format(
                name, feature_name), method='PUT', data={'enabled': True})
            logger.info('Enabled ' + feature_name + ' for ' + name)
            sleep_secs(5, 'waiting for the ' + feature_name + ' to be enabled')
        except Exception as e:
            traceback.print_exc()


def delete_collection(name):
    logger.info('Deleting Collection: ' + name)
    rsp = lweutils.json_http(API_URL + '/collections/' + name, method='DELETE')
    logger.debug('Deleted Collection: ' + name)
    sleep_secs(5, 'waiting for collection to be deleted')


def delete_jobs():
    """delete jobs in the connector."""
    rsp = lweutils.json_http(CONNECTORS_URL + '/jobs/')
    if rsp is None:
        logger.debug('no jobs')
        return
    for job in rsp:
        name = job['id']
        if 'state' in job and job['state'] != 'STOPPED':
            logger.debug('stopping job {}'.format(name))
            rsp = lweutils.json_http(
                CONNECTORS_URL + '/jobs/' + name, method='DELETE')
        # delete the history too.
        rsp = lweutils.json_http(
            HISTORY_URL + '/connectors/items/' + name, method='DELETE')


def list_collection_names():
    rsp = lweutils.json_http(API_URL + '/collections/', method='GET')
    collection_names = [c['id'] for c in rsp]
    logger.debug('collection names: {}'.format(collection_names))
    return collection_names


def get_stock_data(seriesDir, symbol):
    csv_path = seriesDir + '/' + symbol + '.csv'
    if os.path.exists(csv_path):
        cached = open(csv_path)
        logger.debug('Found {} in the cache {}'.format(symbol, csv_path))
        data = cached.read()
    else:
        logger.debug(
            'Could not find {} in the cache {}, so downloading'.format(symbol, csv_path))
        year = datetime.date.today().year
        url = 'http://ichart.finance.yahoo.com/table.csv?s={}&f={}&ignore=.csv'.format(
            symbol, year)
        response = urllib2.urlopen(url)
        data = response.read()
        output = open(csv_path, 'wb')
        output.write(data)
        output.close()
        sleep_secs(1, "so we don't get banned from yahoo")
    return data


def index_historical(solr, stocks, data_source, seriesDir):
    for symbol in stocks:
        logger.info('Indexing: ' + symbol)

        data = get_stock_data(seriesDir, symbol)

        # parse the docs and send to solr
        lines = data.splitlines()
        lines.pop(0)  # pop the first, as it is the list of columns
        for line in lines:
            # logger.debug(l: " + line)
            items = {}
            date, open_val, high, low, close, volume, adj_close = line.split(
                ',')
            items['id'] = symbol + date
            items['symbol'] = symbol
            items['trade_date'] = date + 'T00:00:00Z'
            items['open'] = open_val
            items['high'] = high
            items['low'] = low
            items['close'] = close
            items['volume'] = volume
            items['adj_close'] = adj_close
            # TODO
            # Precompute buckets into the ranges for the buckets

            common_finance.add(
                solr, [items], data_source.datasource_id(), commit=False)
            # Date,Open,High,Low,Close,Volume,Adj Close
            # for r in csv.reader(data, lineterminator='\n'):
            #   print "r: " + str(len(r))
            #date,open_val,high,low,close,volume,adj_close = r
            # print date
    solr.commit()


def create_press_crawler(options, stock):
    # data = {"mapping": {"mappings": {"symbol": "symbol", "open": "open", "high": "high", "low": "low", "close": "close",
    #                 "trade_date":"trade_date",
    #                 "volume": "volume",
    #                 "adj_close": "adj_close"}}}
    url = 'http://finance.yahoo.com/q/p?s={}+Press+Releases'.format(stock)
    include_paths = [
        'http://finance\.yahoo\.com/news/.*',
        'http://m\.yahoo\.com/.*',
        'https://m\.yahoo\.com/.*',
        'http://finance\.yahoo\.com/q/p\?s={}+Press+Releases'.format(stock)]
    name = 'PressRelease_' + stock
    datasource = datasource_connection.create_web(
        name=name, collection=options.finance_collection, start_urls=[url], depth=1, include_regexps=include_paths)
    #rsp = lweutils.json_http(DS_URL + "/datasources/" + id + "/job", method="PUT")
    datasource.start()
    return datasource


def create_press_ds(options, stocks):
    logger.info('Creating Crawler of Press Release data for all symbols')
    stock_lists = list(stocks)
    for stock in stock_lists:
        create_press_crawler(options, stock)


def create_twitter_ds(stocks, collection, access_token, consumer_key, consumer_secret, token_secret):
    logger.info('Creating Twitter Data Source for all symbols')

    # I don't know if this is really necessary yet
    pipeline_name = define_twitter_pipeline(stocks)

    # can only do 400 tracks at a time
    stock_lists = list(stocks)
    length = len(stock_lists)
    if length > 0:
        steps = max(1, length / 100)
        step = 0
        logger.debug('steps={}, len={}'.format(steps, length))
        for i in xrange(steps):
            section = stock_lists[step:step + 100]
            add_twitter(collection, i, section, pipeline_name, stocks, access_token,
                        consumer_key, consumer_secret, token_secret)
            step += 101
        if step < length:
            section = stock_lists[step + 1:]
            add_twitter(collection, i, section, pipeline_name, stocks, access_token,
                        consumer_key, consumer_secret, token_secret)


def should_track(company_name):
    # there are a couple company names we don't want to track; they're too
    # common.
    if company_name.lower() == 'ball' or company_name.lower() == 'ppl':
        return False
    else:
        return True


def add_twitter(collection, i, stock_lists, pipeline_name, stocks, access_token, consumer_key, consumer_secret, token_secret):
    logger.debug('add_twitter #{} {} {}'.format(i, stock_lists, stocks))
    name = 'Twitter_{}'.format(i)
    filters = []
    for symbol in stock_lists:
        if len(symbol) > 1:
            # there are some one-letter stock symbols that are kind of useless
            # to search on
            filters.append('${}'.format(symbol))
        company_name = clean_company_name(stocks[symbol][1])
        if should_track(company_name):
            filters.append(company_name)

    datasource = datasource_connection.create_twitter(name=name, access_token=access_token, consumer_key=consumer_key,
                                                      pipeline=pipeline_name, consumer_secret=consumer_secret,
                                                      token_secret=token_secret, collection=collection, filters=filters)
    datasource.start()


def create_historical_ds(options):
    name = options.historical_datasource_name
    logger.info('Creating DS for {}'.format(name))
    if datasource_connection.get(name) is not None:
        logger.debug('datasource {} already exists'.format(name))
        return
    logger.debug('no existing datasource {}'.format(name))

    pipeline_name = define_historical_pipeline()

    datasource = datasource_connection.create_push(name=name, pipeline=pipeline_name,
                                                   collection=options.finance_collection, port=options.historical_port)
    datasource.start()
    return datasource


def define_historical_pipeline():
    """define historical pipeline.

    Example with explicitly defined fields

    """
    pipeline_name = 'historical'
    if find_pipeline(pipeline_name) is not None:
        logger.debug('pipeline {} already exists'.format(pipeline_name))
        return pipeline_name

    default_solr_pipeline = 'conn_solr'
    # copy and modify this default one
    result = lweutils.json_http(PIPELINE_URL + '/' + default_solr_pipeline)
    result['id'] = pipeline_name
    for stage in result['stages']:
        if stage['id'] == 'conn_mapping':
            mappings = []
            fields = ['open', 'trade_date', 'high',
                      'low', 'close', 'volume', 'adj_close']
            for field in fields:
                mappings.append(
                    {'source': field, 'target': field, 'operation': 'copy'})

            # TODO: HACK. I should not have to worry about this
            add_connector_mappings(mappings)
            stage['mappings'] = mappings
            stage['renameUnknown'] = False

    insert_debug_stage(result)
    logger.debug("saving pipeline '{}': {}".format(pipeline_name, result))
    lweutils.json_http(
        PIPELINE_URL + '/' + pipeline_name, method='PUT', data=result)
    return pipeline_name


def clean_company_name(name):
    """Strips things like "Corp" and "Inc" from the company names, hopefully
    resulting in a more normal name that might appear in news articles or
    Twitter feeds.
    """
    return re.sub(r' (& Co\.?|Corp\.?|Co\.|Cos\.|Groups?\.?|Inc\.?|Intl\.?|Svc\.Gp\.|Ltd\.?|plc\.?)',
                  '', name)

def define_twitter_pipeline(stocks):
    """define twitter pipeline.

    This is a custom pipeline, not based on the default one.

    """
    ticker_symbols = list(stocks)
    company_names = [clean_company_name(s[1]) for s in stocks.values()]

    pipeline_name = 'twitter'
    if find_pipeline(pipeline_name) is not None:
        logger.debug('pipeline {} already exists'.format(pipeline_name))
        return pipeline_name

    pipeline = {'id': pipeline_name,
                'stages': [
                    {'type': 'logging', 'detailed': True},
                    {'type': 'lookup-extractor',
                     'rules': [
                         {'source': ['tweet'],
                          'target': 'named_entities_ss',
                          'case-sensitive': True,
                          'entity-types': {},
                          'additional-entities': {'symbol': ticker_symbols}},
                         {'source': ['tweet'],
                          'target': 'named_entities_ss',
                          'case-sensitive': False,
                          'entity-types': {},
                          'additional-entities': {'company_name': company_names}}
                     ]},
                    {'type': 'field-mapping',
                     'renameUnknown': True,
                     'mappings': [
                         {'source': 'mimeType', 'target': 'mimeType_ss', 'operation': 'move'},
                         {'source': 'userMentionStart_i', 'target': 'userMentionStart_is', 'operation': 'move'},
                         {'source': 'userMentionEnd_i', 'target': 'userMentionEnd_is', 'operation': 'move'},
                         {'source': 'userMentionScreenName_t', 'target': 'userMentionScreenName_txt',
                          'operation': 'move'},
                         {'source': 'userMentionName_t', 'target': 'userMentionName_txt', 'operation': 'move'},
                         {'source': 'tagStart_i', 'target': 'tagStart_is', 'operation': 'move'},
                         {'source': 'tagEnd_i', 'target': 'tagEnd_is', 'operation': 'move'},
                         {'source': 'tagText_s', 'target': 'tagText_ss', 'operation': 'move'},
                         {'source': 'tagText', 'target': 'tagText_ss', 'operation': 'move'},
                         {'source': 'placeCountry_t', 'target': 'placeCountry_txt', 'operation': 'move'},
                         {'source': 'url_s', 'target': 'url_ss', 'operation': 'move'},
                         {'source': 'url', 'target': 'url_ss', 'operation': 'move'},
                         {'source': 'urlExpanded', 'target': 'urlExpanded_ss', 'operation': 'move'},
                         {'source': 'urlExpanded_s', 'target': 'urlExpanded_ss', 'operation': 'move'},
                         {'source': 'urlDisplay', 'target': 'urlDisplay_ss', 'operation': 'move'},
                         {'source': 'urlDisplay_s', 'target': 'urlDisplay_ss', 'operation': 'move'},
                         {'source': 'mediaUrl', 'target': 'mediaUrl_ss', 'operation': 'move'},
                         {'source': 'mediaUrl_s', 'target': 'mediaUrl_ss', 'operation': 'move'},
                         {'source': 'document_fetching_time', 'target': 'document_fetching_time_s',
                          'operation': 'move'},
                         {'source': 'parse_time', 'target': 'parse_time_s', 'operation': 'move'},
                         {'source': 'parsing', 'target': 'parse_s', 'operation': 'move'},
                         {'source': '/(data_source.*)/', 'target': '$1_s', 'operation': 'move'},
                     ]},
                    #{'type': 'logging', 'detailed': True},
                    {'type': 'solr-index'}
                ]}
    logger.debug("saving pipeline '{}': {}".format(pipeline_name, pipeline))
    lweutils.json_http(
        PIPELINE_URL + '/' + pipeline_name, method='PUT', data=pipeline)
    return pipeline_name


def add_connector_mappings(mappings):
    mappings.append({'source': 'document_fetching_time',
                     'target': 'document_fetching_time_s', 'operation': 'move'})
    mappings.append(
        {'source': 'parse_time', 'target': 'parse_time_s', 'operation': 'move'})
    mappings.append(
        {'source': 'parsing', 'target': 'parse_s', 'operation': 'move'})
    mappings.append(
        {'source': '/(data_source.*)/', 'target': '$1_s', 'operation': 'move'})

# temp hack


def command_foo(options):
    define_company_pipeline()


def create_company_ds(options):
    name = options.company_datasource_name
    logger.info('Creating DS for {}'.format(name))
    if datasource_connection.get(name) is not None:
        logger.debug('datasource {} already exists'.format(name))
        return
    logger.debug('no existing datasource {}'.format(name))

    pipeline_name = define_company_pipeline()

    datasource = datasource_connection.create_push(name=name, pipeline=pipeline_name,
                                                   collection=options.finance_collection, port=options.company_port)
    datasource.start()
    return datasource


def find_pipeline(name):
    pipelines = lweutils.json_http(PIPELINE_URL)
    for pipeline in pipelines:
        if 'id' in pipeline and pipeline['id'] == name:
            return pipeline
    return None


def define_company_pipeline():
    """define company pipeline.

    Example with ehr... some defined fields

    """
    pipeline_name = 'company'
    if find_pipeline(pipeline_name) is not None:
        logger.debug('pipeline {} already exists'.format(pipeline_name))
        return pipeline_name

    default_solr_pipeline = 'conn_solr'
    logger.debug("getting default pipeline '{}' to use as a template".format(
        default_solr_pipeline))
    # copy and modify this default one
    result = lweutils.json_http(PIPELINE_URL + '/' + default_solr_pipeline)
    result['id'] = pipeline_name
    for stage in result['stages']:
        if stage['id'] == 'conn_mapping':
            mappings = stage['mappings']
            # TODO: HACK. I should not have to worry about this
            add_connector_mappings(mappings)
            stage['mappings'] = mappings
            stage['renameUnknown'] = False

    insert_debug_stage(result)

    logger.debug("saving pipeline '{}': {}".format(pipeline_name, result))
    lweutils.json_http(
        PIPELINE_URL + '/' + pipeline_name, method='PUT', data=result)
    return pipeline_name


def insert_debug_stage(data):
    # create a detailed logging stage, and insert it before the solr-index
    # stage
    debug_stage = {
        'id': 'index_debugging',
        'type': 'logging',
        'detailed': True
    }
    solr_stage_indexes = [
        i for i, j in enumerate(data['stages']) if j['type'] == 'solr-index']
    if len(solr_stage_indexes) == 0:
        logger.debug('No solr-index stage found')
    solr_stage_index = solr_stage_indexes[0]
    data['stages'].insert(solr_stage_index, debug_stage)


def create_banana_fields(args):
    args.kibana_fields.create('user')
    args.kibana_fields.create('group')
    args.kibana_fields.create('dashboard', indexed=False)


def create_fields(args):
    create_banana_fields(args)
    # Twitter

    # Company info
    # Symbol,Company,Industry,City,State
    args.finance_fields.create('RESULT_TYPE')
    args.finance_fields.create('data_source_name', copy_fields='RESULT_TYPE')
    args.finance_fields.create('symbol')

    args.finance_fields.create('industry_facet')
    args.finance_fields.create(
        'industry', 'type=text_en', copy_fields='industry_facet')

    args.finance_fields.create('company_facet', type='string')
    args.finance_fields.create(
        'company', 'type=text_en', copy_fields='company_facet')

    args.finance_fields.create('city_facet')
    args.finance_fields.create(
        'city', type='text_en', copy_fields='city_facet')

    args.finance_fields.create('hierarchy', multi_valued=True)

    args.finance_fields.create('state')

    # Historical
    create_bucket_field(args, 'open', 'float')
    create_bucket_field(args, 'trade_date', 'date')
    create_bucket_field(args, 'high', 'float')
    create_bucket_field(args, 'low', 'float')
    create_bucket_field(args, 'close', 'float')
    create_bucket_field(args, 'volume', 'long')
    create_bucket_field(args, 'adj_close', 'float')

    # Intra Day
    create_bucket_field(args, 'quote_date', 'date')
    # create_bucket_field(args, "price", "date")   # TODO: huh?


def create_bucket_field(args, field, type):
    args.finance_fields.create(field + '_bucket')
    args.finance_fields.create(field, type=type)

#########################################

p = argparse.ArgumentParser(description='Setup Apollo Financial Demo.')

p.add_argument('--twitter', action='store_true',
               help='create the twitter datasource')
p.add_argument('--access_token', metavar='token', help='Twitter access token')
p.add_argument('--consumer_key', metavar='key', help='Twitter consumer key')
p.add_argument(
    '--consumer_secret', metavar='secret', help='Twitter consumer secret')
p.add_argument('--token_secret', metavar='token', help='Twitter token secret')

p.add_argument('--data_dir', metavar='dir', default='../../../data',
               help='historical data directory (default: ../../../data)')

p.add_argument('--api_host', metavar='host', dest='host', default='localhost',
               help='Apollo backend API host (default: localhost)')
p.add_argument('--api_port', type=int, metavar='port', dest='api_port', default='8765',
               help='Apollo backend API port (default: 8765)')

p.add_argument('--ui_host', metavar='host', dest='ui_host', default='localhost',
               help='UI host (default: localhost)')  # TODO: is this Apollo-admin or something else?
p.add_argument('--ui_port', type=int, metavar='port', dest='ui_port', default='8989',
               help='UI host (default: 8989)')  # TODO: is this Apollo-admin or something else?

p.add_argument('--solr_host', metavar='host', dest='solr_host', default='localhost',
               help='Solr host (default: localhost)')
p.add_argument('--solr_port', type=int, metavar='port', dest='solr_port', default='8983',
               help='Solr port (default: 8983)')

p.add_argument('--connectors_host', metavar='host', default='localhost',
               help='Connectors host (default: localhost)')
p.add_argument('--connectors_port', type=int, metavar='port', dest='connectors_port', default='8984',
               help='Connectors port (default: 8984)')

p.add_argument('--external', action='store_true',
               help='create the external datasource')
p.add_argument('--fields', action='store_true',
               help='create the fields')

p.add_argument('--finance-collection', metavar='name', default='Finance',
               help='name of the financia collection (default: Finance)')
p.add_argument('--kibana-collection', metavar='name', default='kibana-int',
               help='name of the Kibana collection (default: kibana-int)')
p.add_argument('--company_datasource_name', metavar='name', default='Company',
               help='name of the company datasource (default: Company)')
p.add_argument('--historical_datasource_name', metavar='name', default='HistoricalPrices',
               help='name of the historical datasource (default: HistoricalPrices)')

p.add_argument('--create', action='store_true', dest='create',
               help='create collections and datasources')
p.add_argument('--action', action='append', dest='action', choices=['setup', 'delete', 'reindex', 'foo', 'help'],
               help='the main action (default: setup)')

p.add_argument('--company_port', type=int, dest='company_port', default='9191',
               metavar='port',
               help='connectors solr update handler port for Company datasource')
p.add_argument('--historical_port', type=int, dest='historical_port', default='9898',
               help='connectors solr update handler port for History datasource',
               metavar='port')

p.add_argument('--stocks_file', type=file, metavar='file',
               default='../../../data/sp500List-30.txt',
               help='filename of the stocks file')

p.add_argument('--press', action='store_true', help='create press crawler')
p.add_argument('--index', action='store_true', help='index the content')

args = p.parse_args()

# TODO: FIX UP ALL THIS HACKY VARIABLE STUFF
COLLECTION = args.finance_collection
LWS_URL = 'http://{}:{}/lucid'.format(args.host, args.api_port)
API_URL = LWS_URL + '/api/v1'
SOLR_URL = 'http://{}:{}/solr/{}'.format(
    args.solr_host, args.solr_port, COLLECTION)
COL_URL = API_URL + '/collections/' + COLLECTION
FIELDS_URL = SOLR_URL + '/schema/fields'

CONNECTORS_URL = 'http://{}:{}/connectors/api/v1/connectors'.format(
    args.connectors_host, args.connectors_port)
HISTORY_URL = 'http://{}:{}/connectors/api/v1/history'.format(
    args.connectors_host, args.connectors_port)
PIPELINE_URL = 'http://{}:{}/connectors/api/v1/index-pipelines'.format(
    args.connectors_host, args.connectors_port)

args.kibana_fields_url = 'http://{}:{}/solr/kibana-int/schema/fields'.format(
    args.solr_host, args.solr_port)
args.company_solr_url = 'http://{}:{}/solr'.format(
    args.host, args.company_port)
args.historical_solr_url = 'http://{}:{}/solr'.format(
    args.host, args.historical_port)

lweutils.UI_URL = 'http://{}:{}'.format(args.ui_host, args.ui_port)
lweutils.UI_API_URL = lweutils.UI_URL + '/lucid/api/v1'

logger.debug('creating datasource connection {}'.format(CONNECTORS_URL))
datasource_connection = datasource.DataSourceConnection(CONNECTORS_URL)
logger.debug('created datasource connection')

# TODO: these should be member variables on an object, not args
args.finance_fields = fields.FieldsConnection(
    'http://{}:{}/solr/{}/schema/fields'.format(args.solr_host, args.solr_port, args.finance_collection))
args.kibana_fields = fields.FieldsConnection(
    'http://{}:{}/solr/{}/schema/fields'.format(args.solr_host, args.solr_port, args.kibana_collection))

if args.action is None:
    args.action = ['setup']
for action in args.action:
    func = 'command_' + action
    logger.debug('running {}'.format(func))
    vars()[func](args)
