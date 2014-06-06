import argparse
import httplib2
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

class DemoSetup:

    def command_setup(self):

        self.load_stocks()
        self.get_solr()

        self.create_collection(self.args.finance_collection)

        if self.args.fields and self.args.create:
            self.create_fields()
        if self.args.twitter and self.args.create:
            self.create_twitter_ds()
        if self.args.press and self.args.create:
            self.create_press_ds()
        historical_data_source = None
        company_datasource = None
        if self.args.external:
            historical_data_source = self.create_historical_ds()
            company_datasource = self.create_company_ds()
        if self.args.index:
            if company_datasource == None:
                company_datasource = self.datasource_connection.get(
                    self.args.company_datasource_name)
            if company_datasource:
                logger.info('Indexing for data source {}'.format(
                    company_datasource.datasource_id()))
                company_solr = pysolr.Solr(self.company_solr_url, timeout=10)
                self.index_stocks(company_solr, company_datasource)
            else:
                logger.error(
                    "Couldn't find datasource {}".format(self.args.company_datasource_name))

            if historical_data_source == None:
                historical_data_source = self.datasource_connection.get(
                    self.args.historical_datasource_name)
            if historical_data_source:
                logger.info('Indexing for data source {}'.format(
                    historical_data_source.datasource_id()))
                historical_solr = pysolr.Solr(
                    self.historical_solr_url, timeout=10)
                self.index_historical(
                    historical_solr, historical_data_source)
            else:
                logger.error("Couldn't find datasource {}".format(
                    self.args.historical_datasource_name))
            self.get_solr().commit()        

    def command_reindex(self):
        self.get_solr()
        self.load_stocks()
        historical_datasource = self.datasource_connection.get(
            self.args.historical_datasource_name)
        if historical_datasource:
            logger.info(
                'Reindexing for data source: ' + historical_datasource.datasource_id())
            self.index_historical(self.solr, historical_datasource)
        else:
            logger.error(
                "Couldn't find datasource {}".format(self.args.company_datasource_name))

    def command_delete(self):
        self.delete_datasources()
        self.delete_jobs()
        self.delete_collections()
        self.delete_pipelines()

    def command_help(self):
        self.p.print_help()

    def load_stocks(self):
        """Load the stocks from the stocklist."""
        logger.debug('loading stocks from {}'.format(self.args.stocks_file))
        self.stocks = common_finance.load_stocks(self.args.stocks_file)
        logger.debug('loaded {} stocks: {}'.format(len(self.stocks), self.stocks))

    def get_solr(self):
        """Get the solr client."""
        if not hasattr(self, 'solr'):
            logger.debug('creating PySolr client for {}'.format(self.solr_url))
            self.solr = pysolr.Solr(self.solr_url, timeout=10)
            logger.debug('created PySolr client')
        return self.solr

    def delete_datasources(self):
        datasources = self.datasource_connection.datasources()
        logger.debug('datasources={}'.format(datasources))
        for datasource in datasources.values():
            if datasource.datasource_id() in self.datasource_names or re.match(r'Twitter_\d+', datasource.datasource_id()):
                datasource.delete()
            else:
                logger.info('skipping datasource {}'.format(datasource))

    def delete_collections(self):
        collections = [c for c in self.list_collection_names() if c in self.collections]
        for collection_name in collections:
            self.delete_collection(collection_name)


    def delete_pipelines(self):
        pipelines = lweutils.json_http(self.pipeline_url)
        for pipeline in pipelines:
            # TODO: get this from somewhere
            if pipeline['id'] in ['company', 'historical', 'twitter']:
                lweutils.json_http(
                    self.pipeline_url + '/' + pipeline['id'], method='DELETE')

    def index_stocks(self, solr, data_source):
        logger.info('Indexing Company Info')
        for symbol in self.stocks.keys():
            try:
                (sym, company_name, industry, city, state) = self.stocks[symbol]
                items = {'id': symbol,
                         'symbol': symbol,
                         'company': company_name,
                         'industry': industry,
                         'city': city,
                         'state': state,
                         'hierarchy': [
                             '1/' + industry,
                             '2/' + state,
                             '3/' + city]}  # Start at 1/ for ease integration w/ JS
            except Exception as e:
                logger.error(
                    'Error while parsing stock {} with values {}'.format(symbol, self.stocks[symbol]))
                traceback.print_exc()
            logger.debug("adding to solr: {}".format(items))
            common_finance.add(
                solr, [items], data_source.datasource_id(), commit=False)

    def collection_exists(self, name):
        logger.info('checking for collection: ' + name)
        rsp = lweutils.json_http(self.api_url + '/collections', method='GET')
        logger.debug('collections: {}'.format(rsp))
        for collection in rsp:
            if 'id' not in collection:
                logger.error('No id in collection')
            if collection['id'] == name:
                logger.debug('collection {} exists'.format(name))
                return True
        return False

    def create_collection(self, name):
        if self.collection_exists(name):
            logger.info('collection {} already exists'.format(name))
        else:
            logger.info('Creating New Collection: {}'.format(name))
            data = {'name': name}
            try:
                rsp = lweutils.json_http(
                    self.api_url + '/collections/' + name, method='PUT', data=data)
                logger.info('Created New Collection: {}'.format(name))
                # otherwise enable_dynamic_schema will fail saying the schema is
                # immutable
                sleep_secs(5, 'waiting for collection to get created')
            except Exception as e:
                traceback.print_exc()

        self.enable_feature(name, 'dynamicSchema')
        self.enable_feature(name, 'signals')

    def is_feature_enabled(self, coll_name, feature_name):
        rsp = lweutils.json_http(
            self.api_url + '/collections/{}/features'.format(coll_name))
        for feature in rsp:
            if feature['name'] == feature_name:
                logger.debug('{}={}'.format(feature_name, feature['name']))
                return feature['enabled']
        return False

    def enable_feature(self, name, feature_name):
        if self.is_feature_enabled(name, feature_name):
            logger.info(
                '{} already enabled for collection {}'.format(feature_name, name))
        else:
            try:
                logger.info('Enabling ' + feature_name + ' for ' + name)
                rsp = lweutils.json_http(self.api_url + '/collections/{0}/features/{1}'.format(
                    name, feature_name), method='PUT', data={'enabled': True})
                logger.info('Enabled ' + feature_name + ' for ' + name)
                sleep_secs(5, 'waiting for the ' + feature_name + ' to be enabled')
            except Exception as e:
                traceback.print_exc()

    def delete_collection(self, name):
        logger.info('Deleting Collection: ' + name)
        rsp = lweutils.json_http(self.api_url + '/collections/' + name, method='DELETE')
        logger.debug('Deleted Collection: ' + name)
        sleep_secs(5, 'waiting for collection to be deleted')

    def delete_jobs(self):
        """delete jobs in the connector."""
        rsp = lweutils.json_http(self.connectors_url + '/jobs/')
        if rsp is None:
            logger.debug('no jobs')
            return
        for job in rsp:
            name = job['id']
            if 'state' in job and job['state'] != 'STOPPED':
                logger.debug('stopping job {}'.format(name))
                rsp = lweutils.json_http(
                    self.connectors_url + '/jobs/' + name, method='DELETE')
            # delete the history too.
            rsp = lweutils.json_http(
                self.historical_url + '/connectors/items/' + name, method='DELETE')

    def list_collection_names(self):
        rsp = lweutils.json_http(self.api_url + '/collections/', method='GET')
        collection_names = [c['id'] for c in rsp]
        logger.debug('collection names: {}'.format(collection_names))
        return collection_names

    def get_stock_data(self, seriesDir, symbol):
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

    def index_historical(self, solr, data_source):
        for symbol in self.stocks.keys():
            logger.info('Indexing: ' + symbol)

            data = self.get_stock_data(self.args.data_dir, symbol)

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

    def create_press_crawler(self, stock):
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

        datasource = self.datasource_connection.create_web(
            name=name, collection=self.args.finance_collection, start_urls=[url], depth=1, include_regexps=include_paths)
        #rsp = lweutils.json_http(DS_URL + "/datasources/" + id + "/job", method="PUT")
        datasource.start()
        return datasource

    def create_press_ds(self):
        logger.info('Creating Crawler of Press Release data for all symbols')
        for stock in self.stocks.keys():
            self.create_press_crawler(stock)

    def create_twitter_ds(self):
        logger.info('Creating Twitter Data Source for all symbols')

        # I don't know if this is really necessary yet
        pipeline_name = self.define_twitter_pipeline()

        # can only do 100 tracks at a time, so split the stock list into sublists
        stock_symbols = self.stocks.keys()
        sublist_max=100
        sublists = [stock_symbols[x:x+sublist_max] for x in xrange(0, len(stock_symbols), sublist_max)]
        for i, sublist in enumerate(sublists):
            self.add_twitter(i, sublist, pipeline_name)

    def add_twitter(self, i, stock_list, pipeline_name):
        logger.debug('add_twitter #{} {}'.format(i, stock_list))
        name = 'Twitter_{}'.format(i)
        filters = []
        for symbol in stock_list:
            if len(symbol) > 1:
                # there are some one-letter stock symbols that are kind of useless
                # to search on
                filters.append('${}'.format(symbol))
            company_name = self.clean_company_name(self.stocks[symbol][1])
            filters.append(company_name)

        datasource = self.datasource_connection.create_twitter(name=name,
            collection=self.args.finance_collection,
            filters=filters,
            pipeline=pipeline_name,
            access_token=self.args.twitter_access_token,
            consumer_key=self.args.twitter_consumer_key,
            consumer_secret=self.args.twitter_consumer_secret,
            token_secret=self.args.twitter_token_secret)
        datasource.start()

    def create_historical_ds(self):
        name = self.args.historical_datasource_name
        logger.info('Creating DS for {}'.format(name))
        if self.datasource_connection.get(name) is not None:
            logger.debug('datasource {} already exists'.format(name))
            return
        logger.debug('no existing datasource {}'.format(name))

        pipeline_name = self.define_historical_pipeline()

        datasource = self.datasource_connection.create_push(name=name, pipeline=pipeline_name,
                                                            collection=self.args.finance_collection,
                                                            port=self.args.historical_port)
        datasource.start()
        return datasource

    def define_historical_pipeline(self):
        """define historical pipeline.

        Example with explicitly defined fields

        """
        pipeline_name = 'historical'
        if self.find_pipeline(pipeline_name) is not None:
            logger.debug('pipeline {} already exists'.format(pipeline_name))
            return pipeline_name

        default_solr_pipeline = 'conn_solr'
        # copy and modify this default one
        result = lweutils.json_http(self.pipeline_url + '/' + default_solr_pipeline)
        result['id'] = pipeline_name
        for stage in result['stages']:
            if stage['id'] == 'conn_mapping':
                mappings = []
                fields = ['open', 'trade_date', 'high',
                          'low', 'close', 'volume', 'adj_close']
                for field in fields:
                    mappings.append(
                        {'source': field, 'target': field, 'operation': 'copy'})

                self.add_connector_mappings(mappings)
                stage['mappings'] = mappings
                stage['unmapped'] = None

        self.insert_debug_stage(result)
        logger.debug("saving pipeline '{}': {}".format(pipeline_name, result))
        lweutils.json_http(
            self.pipeline_url + '/' + pipeline_name, method='PUT', data=result)
        return pipeline_name

    def clean_company_name(self, name):
        """Strips things like "Corp" and "Inc" from the company names,
        hopefully resulting in a more normal name that might appear in news
        articles or Twitter feeds.
        """
        if re.match(r'(Coach .*|PPL.*|Ball.*)', name):
            return name
        return re.sub(r' (& Co\.?$|Corp\.?$|Co\. Inc\.$|Co\.$|Cos\.$|Groups?\.?$|Inc\.?$|Intl\.?$|Svc\.Gp\.$|Ltd\.?$|plc\.?$)',
                      '', name)

    def define_twitter_pipeline(self):
        """define twitter pipeline.

        This is a custom pipeline, not based on the default one.

        """
        ticker_symbols = self.stocks.keys()
        company_names = [self.clean_company_name(s[1]) for s in self.stocks.values()]

        pipeline_name = 'twitter'
        if self.find_pipeline(pipeline_name) is not None:
            logger.debug('pipeline {} already exists'.format(pipeline_name))
            return pipeline_name

        default_solr_pipeline = 'conn_solr'
        # copy and modify this default one
        pipeline = lweutils.json_http(self.pipeline_url + '/' + default_solr_pipeline)
        pipeline['id'] = pipeline_name

        pipeline_stages = [
            {
                'type': 'lookup-extractor',
                'rules': [
                    {
                        'source': ['tweet'],
                        'target': 'named_entities_ss',
                        'case-sensitive': True,
                        'entity-types': {},
                        'additional-entities': {'symbol': ticker_symbols}
                    },
                    {
                        'source': ['tweet'],
                        'target': 'named_entities_ss',
                        'case-sensitive': False,
                        'entity-types': {},
                        'additional-entities': {'company_name': company_names}
                    }
                ]
            }]

        # nlp stages go first and all other stages come next.
        for each_stage in pipeline['stages']:
            pipeline_stages.append(each_stage)
        pipeline['stages'] = pipeline_stages

        logger.debug("saving pipeline '{}': {}".format(pipeline_name, pipeline))
        lweutils.json_http(
            self.pipeline_url + '/' + pipeline_name, method='PUT', data=pipeline)
        return pipeline_name

    def add_connector_mappings(self, mappings):
        """Add mappings for fields added by connectors framework itself.

        TODO: Connectors should do something sensible by default so that
        I don't need to worry about this.

        """
        mappings.append({'source': 'document_fetching_time',
                         'target': 'document_fetching_time_s', 'operation': 'move'})
        mappings.append(
            {'source': 'parse_time', 'target': 'parse_time_s', 'operation': 'move'})
        mappings.append(
            {'source': 'parsing_time', 'target': 'parsing_time_s', 'operation': 'move'})
        mappings.append(
            {'source': 'parsing', 'target': 'parse_s', 'operation': 'move'})
        mappings.append(
            {'source': '/(data_source.*)/', 'target': '$1_s', 'operation': 'move'})

    def create_company_ds(self):
        name = self.args.company_datasource_name
        logger.info('Creating DS for {}'.format(name))
        if self.datasource_connection.get(name) is not None:
            logger.debug('datasource {} already exists'.format(name))
            return
        logger.debug('no existing datasource {}'.format(name))

        pipeline_name = self.define_company_pipeline()

        datasource = self.datasource_connection.create_push(name=name, pipeline=pipeline_name,
                                                            collection=self.args.finance_collection,
                                                            port=self.args.company_port)
        datasource.start()
        return datasource

    def find_pipeline(self, name):
        pipelines = lweutils.json_http(self.pipeline_url)
        for pipeline in pipelines:
            if 'id' in pipeline and pipeline['id'] == name:
                return pipeline
        return None

    def define_company_pipeline(self,):
        """define company pipeline.

        Example with ehr... some defined fields

        """
        pipeline_name = 'company'
        if self.find_pipeline(pipeline_name) is not None:
            logger.debug('pipeline {} already exists'.format(pipeline_name))
            return pipeline_name

        default_solr_pipeline = 'conn_solr'
        logger.debug("getting default pipeline '{}' to use as a template".format(
            default_solr_pipeline))
        # copy and modify this default one
        result = lweutils.json_http(self.pipeline_url + '/' + default_solr_pipeline)
        result['id'] = pipeline_name
        for stage in result['stages']:
            if stage['id'] == 'conn_mapping':
                mappings = stage['mappings']
                self.add_connector_mappings(mappings)
                stage['mappings'] = mappings
                stage['unmapped'] = None
            elif stage['id'] == 'conn_multivalue_resolver':
                # set the strategy to DEFAULT, because the default is PICK_LAST,
                # which means multiValued fields like "hierarchy" lose all but
                # the last value
                stage['typeStrategy'] = { 'string': 'DEFAULT' }

        self.insert_debug_stage(result)

        logger.debug("saving pipeline '{}': {}".format(pipeline_name, result))
        lweutils.json_http(
            self.pipeline_url + '/' + pipeline_name, method='PUT', data=result)
        return pipeline_name

    def insert_debug_stage(self, data):
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

    def create_fields(self):
        # Company info
        # Symbol,Company,Industry,City,State
        self.finance_fields.create('RESULT_TYPE')
        self.finance_fields.create('data_source_name', copy_fields='RESULT_TYPE')
        self.finance_fields.create('symbol')

        self.finance_fields.create('industry_facet')
        self.finance_fields.create(
            'industry', 'type=text_en', copy_fields='industry_facet')

        self.finance_fields.create('company_facet', type='string')
        self.finance_fields.create(
            'company', 'type=text_en', copy_fields='company_facet')

        self.finance_fields.create('city_facet')
        self.finance_fields.create(
            'city', type='text_en', copy_fields='city_facet')

        self.finance_fields.create('hierarchy', multi_valued=True)

        self.finance_fields.create('state')

        # Historical
        self.create_bucket_field('open', 'float')
        self.create_bucket_field('trade_date', 'date')
        self.create_bucket_field('high', 'float')
        self.create_bucket_field('low', 'float')
        self.create_bucket_field('close', 'float')
        self.create_bucket_field('volume', 'long')
        self.create_bucket_field('adj_close', 'float')

        # Intra Day
        self.create_bucket_field('quote_date', 'date')
        # create_bucket_field("price", "date")   # TODO: huh?

    def create_bucket_field(self, field, type):
        self.finance_fields.create(field + '_bucket')
        self.finance_fields.create(field, type=type)

    def __init__(self, args):
        self.p = argparse.ArgumentParser(description='Setup Apollo Financial Demo.')

        self.p.add_argument('--twitter', action='store_true',
                            help='create the twitter datasource')
        self.p.add_argument('--access_token', metavar='token', dest='twitter_access_token', help='Twitter access token')
        self.p.add_argument('--consumer_key', metavar='key', dest='twitter_consumer_key', help='Twitter consumer key')
        self.p.add_argument(
            '--consumer_secret', metavar='secret', dest='twitter_consumer_secret', help='Twitter consumer secret')
        self.p.add_argument('--token_secret', metavar='token', dest='twitter_token_secret', help='Twitter token secret')

        self.p.add_argument('--data_dir', metavar='dir', default='../../../data',
                            help='historical data directory (default: ../../../data)')

        self.p.add_argument('--api_host', metavar='host', dest='host', default='localhost',
                            help='Apollo backend API host (default: localhost)')
        self.p.add_argument('--api_port', type=int, metavar='port', dest='api_port', default='8765',
                            help='Apollo backend API port (default: 8765)')

        self.p.add_argument('--solr_host', metavar='host', dest='solr_host', default='localhost',
                            help='Solr host (default: localhost)')
        self.p.add_argument('--solr_port', type=int, metavar='port', dest='solr_port', default='8983',
                            help='Solr port (default: 8983)')

        self.p.add_argument('--connectors_host', metavar='host', default='localhost',
                            help='Connectors host (default: localhost)')
        self.p.add_argument('--connectors_port', type=int, metavar='port', dest='connectors_port', default='8984',
                            help='Connectors port (default: 8984)')

        self.p.add_argument('--external', action='store_true',
                            help='create the external datasource')
        self.p.add_argument('--fields', action='store_true',
                            help='create the fields')

        self.p.add_argument('--finance-collection', metavar='name', default='Finance',
                            help='name of the financia collection (default: Finance)')
        self.p.add_argument('--company_datasource_name', metavar='name', default='Company',
                            help='name of the company datasource (default: Company)')
        self.p.add_argument('--historical_datasource_name', metavar='name', default='HistoricalPrices',
                            help='name of the historical datasource (default: HistoricalPrices)')

        self.p.add_argument('--create', action='store_true', dest='create',
                            help='create collections and datasources')
        self.p.add_argument('--action', action='append', dest='actions',
                            choices=['setup', 'delete', 'reindex', 'help'],
                            help='the main action (default: setup)')

        self.p.add_argument('--company_port', type=int, dest='company_port', default='9191',
                            metavar='port',
                            help='connectors solr update handler port for Company datasource')
        self.p.add_argument('--historical_port', type=int, dest='historical_port', default='9898',
                            help='connectors solr update handler port for History datasource',
                            metavar='port')

        self.p.add_argument('--stocks_file', type=file, metavar='file',
                            default='../../../data/sp500List-30.txt',
                            help='filename of the stocks file')

        self.p.add_argument('--press', action='store_true', help='create press crawler')
        self.p.add_argument('--index', action='store_true', help='index the content')

        logger.debug("parsing {}".format(args))
        self.args = self.p.parse_args(args)

        self.api_url = 'http://{}:{}/lucid/api/v1'.format(self.args.host, self.args.api_port)
        self.solr_url = 'http://{}:{}/solr/{}'.format(
            self.args.solr_host, self.args.solr_port, self.args.finance_collection)
        self.connectors_url = 'http://{}:{}/connectors/api/v1/connectors'.format(
            self.args.connectors_host, self.args.connectors_port)
        self.historical_url = 'http://{}:{}/connectors/api/v1/history'.format(
            self.args.connectors_host, self.args.connectors_port)
        self.pipeline_url = 'http://{}:{}/connectors/api/v1/index-pipelines'.format(
            self.args.connectors_host, self.args.connectors_port)

        self.company_solr_url = 'http://{}:{}/solr'.format(
            self.args.host, self.args.company_port)
        self.historical_solr_url = 'http://{}:{}/solr'.format(
            self.args.host, self.args.historical_port)

        logger.debug('creating datasource connection {}'.format(self.connectors_url))
        self.datasource_connection = datasource.DataSourceConnection(self.connectors_url)
        logger.debug('created datasource connection')

        self.finance_fields = fields.FieldsConnection(
            'http://{}:{}/solr/{}/schema/fields'.format(self.args.solr_host, self.args.solr_port, self.args.finance_collection))

        self.collections = (self.args.finance_collection)
        self.datasource_names = (self.args.company_datasource_name, self.args.historical_datasource_name)

        if self.args.actions is None or len(self.args.actions) == 0:
            self.args.actions = ['setup']

    def run(self):
        """Invoke the command specific by the action argument, e.g.:
        command_setup()."""
        for action in self.args.actions:
            func_name = 'command_' + action
            logger.debug('running {}'.format(func_name))
            func = getattr(self, func_name)
            logger.debug('func {}'.format(func))
            func()

if __name__ == '__main__':
    demoSetup = DemoSetup(sys.argv[1:])
    demoSetup.run()
