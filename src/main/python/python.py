import optparse
from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
import pysolr
from jinja2 import Environment
from pysolr import Results
import math
import datetime
import re


app = Flask(__name__)
environment = Environment()

FQ_PATTERN = re.compile("f=(\w+)")
@app.template_filter('split_category_facet')
def split_category_facet(facet):
    """
    Splits an FQ string into it's parts.  FQs look like :
    {!raw f=depthCategoryNames}2/Movies & Music
    """
    #TODO: CHECK if it is splittable first
    if (facet.find("}") != -1):
        splits = facet.split("}")
        match = FQ_PATTERN.search(splits[0])
        if (match):
            facet_name = match.group(1)
        else:
            print("Couldn't find a facet name")
            facet_name = "depthCategoryNames"
        facet_value = splits[1]
        facet_depth = facet_value.split('/')[0]
        return facet_name, facet_value, facet_depth

    return facet

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d-%m-%Y'):
    return value.strftime(format)

@app.template_filter('datetimeformatstr')
def datetimeformatstr(value, format='%d-%m-%Y', input='%Y-%m-%dT%H:%M:%SZ'):
    #2013-11-20T21:41:34.821Z
    return datetime.datetime.strptime(value, input).strftime(format)




def process_solr_rsp(solr_rsp):
    result_kwargs = {}
    if solr_rsp.get('debug'):
        result_kwargs['debug'] = solr_rsp['debug']
    if solr_rsp.get('highlighting'):
        result_kwargs['highlighting'] = solr_rsp['highlighting']
    if solr_rsp.get('facet_counts'):
        result_kwargs['facets'] = solr_rsp['facet_counts']
    if solr_rsp.get('spellcheck'):
        result_kwargs['spellcheck'] = solr_rsp['spellcheck']
    if solr_rsp.get('stats'):
        result_kwargs['stats'] = solr_rsp['stats']
    if 'QTime' in solr_rsp.get('responseHeader', {}):
        result_kwargs['qtime'] = solr_rsp['responseHeader']['QTime']
    if solr_rsp.get('grouped'):
        result_kwargs['grouped'] = solr_rsp['grouped']
    return result_kwargs;

@app.route('/hierarchical_facets')
def hierarchical_facets():
    #page_results = results
    # Solr query params
    solr_params = {
                  'qt' : '/lucid',
                  'facet' : 'true',
                  'rows' : 0,
                  'facet.field' : 'hierarchy',
                  'facet.sort' : 'count',
                  'facet.limit' : '15',
                  'facet.mincount' : '1',
                }

    if not request.args:
        solr_params['q'] = '*:*'
        solr_params['start'] = 0
        solr_params['fq'] = []
    else:
        args = request.args
        if args.has_key('q'):
            solr_params['q'] = args.get('q')
        else:
            solr_params['q'] = '*:*'
        if args.has_key('fq'):
            print(args.get('fq'))
            solr_params['fq'] = args.get('fq')
        if args.has_key('facet.prefix'):
            solr_params['facet.prefix'] = args.get('facet.prefix')
        else:
            solr_params['facet.prefix'] = "0/"

    facet_results = solr._select(solr_params)
    return facet_results

@app.route('/', methods=['POST', 'GET'])
def standard(name=None):
    # do a match all request
    query = "*:*"
    start = 0
    if request.method == 'POST' and request.form['search_box']:
        query = request.form['search_box']
    else:
        if request.args.get('q'):
            query = request.args.get('q')

    if request.args.get('start'):
        start = request.args.get('start')
    fq = []
    if request.args.get('fq'):
        fq = request.args.getlist('fq')
    active = "Results"
    if request.args.get('active'):
        active = request.args.get('active')

    dsn_results = "data_source_name:HistoricalPrices"

    source_filters = []
    group = "false"
    group_field = "symbol"
    if active == "Results":
        source_filters.append("-" + dsn_results)
    else:#Historical, do grouping
        source_filters.append(dsn_results)
        group = "true"

# &facet.date=timestamp&facet.date.start=2013-10-08T14:17:49.04Z&facet.date.end=NOW/DAY%2B1DAY&facet.date.gap=%2B1HOUR
    app.logger.info("Query: " + query)
    kwargs = {"qt": "/lucid", "facet": "true", "start": start, "fl":"*,score",
              # &facet.date=timestamp&facet.date.start=NOW/DAY-1DAY&facet.date.end=NOW/DAY%2B1DAY&facet.date.gap=%2B1HOUR
            "facet.date":"timestamp", "facet.date.start":"NOW/DAY-30DAY", "facet.date.end":"NOW/DAY+1DAY", "facet.date.gap":"+1DAY",
            "facet.date.other":"all",
              "facet.range":["open", "close", "volume"],
              "facet.range.start":"0",
              "facet.range.end":"1000",
              "facet.range.gap":"100",
              "facet.range.other":"all",
              "facet.mincount":"1",
              "f.open.facet.limit":"5",
              "f.close.facet.limit":"5",
              "f.close.open.limit":"5",
              "f.volume.facet.limit":"5",
              "f.volume.facet.range.gap":"500000",
              "f.volume.facet.range.start":"10000",
              "f.volume.facet.range.end":"5000000",
              "facet.pivot":["open,close,volume", "attr_retweetcount,attr_username"],
              "sort":"timestamp desc",
              "stats":"true",
              "group":group,
              "group.field":group_field,
              "group.limit":10,
              "group.sort":"trade_date desc",
              "stats.field":["open", "close","volume"],
              "fq":source_filters
        }

    if fq:
        kwargs['fq'] = fq


    params = {'q': query}
    params.update(kwargs)
    solr_rsp = solr._select(params)
    result = solr.decoder.decode(solr_rsp)
    response = result.get('response') or {}
    facets = result.get('facet_counts') or {}
    stats = result.get('stats') or {}
    grouped = result.get("grouped")
    #app.logger.info("Facets: " + facets)
    numFound = response.get('numFound', 0)
    result_kwargs = process_solr_rsp(result)

    results = Results(response.get('docs', ()), numFound, **result_kwargs)
    page_count = int(math.ceil(numFound / 10.0))
    start = response.get('start', 0)
    current_page_number = int(math.ceil(start/10.0))
    if page_count > 0:
        current_page_number += 1
    else:
        current_page_number = 1
        page_count = 1
    #page_count = (int) Math.ceil(results_found / (double) results_per_page);
    #current_page_number = (int) Math.ceil(start / (double) results_per_page) + (page_count > 0 ? 1 : 0);
    #
    #app.logger.info("Saw {0} result(s).".format(len(results)))
    next_start = start+10
    prev_start = max(start - 10, 0)
    filter_urls = {}
    if fq:
        i = 0
        filter_base_url = url_for('standard', start=str(start), q=query)
        for outer in fq:
            filter_urls[outer] = filter_base_url
            for inner in fq:
                if outer != inner:
                    app.logger.info("Inner: " + inner)
                    filter_urls[outer] += "&fq=" + inner
            i += 1

    current_url = url_for('standard', start=str(start), q=query, fq=fq, active=active)
    results_url = url_for('standard', start=str(start), q=query, fq=fq, active="Results")
    historical_url = url_for('standard', start=str(start), q=query, fq=fq, active="Historical")
    next_url = url_for('standard', start=str(next_start), q=query, fq=fq, active=active)
    prev_url = url_for('standard', start=str(prev_start), q=query, fq=fq, active=active)
    app.logger.info("Next: " + next_url)
    return render_template('standard.jinja2', name=name, search_results=results,
                           fq=fq,
                           grouped=grouped,
                           active=active,
                           filter_urls=filter_urls,
                           raw_response=response,
                           start=start,
                           current_url=current_url, historical_url=historical_url, results_url=results_url,
                           the_facets=facets,
                           the_stats=stats,
                           the_query=query, current_page=current_page_number,
                           next_url=next_url,
                           prev_url=prev_url,
                           the_page_count=page_count)

if __name__ == '__main__':
    p = optparse.OptionParser()
    p.add_option("--api_host", action="store", dest="host", default="localhost")
    p.add_option("-l", "--collection", action="store", dest="collection") #create the collection
    p.add_option("--api_port", action="store", dest="api_port", default="8888")
    opts, args = p.parse_args()
    COLLECTION = opts.collection
    if COLLECTION is None:
        COLLECTION = "Finance"

    LWS_URL = "http://" + opts.host + ":" + opts.api_port
    API_URL = LWS_URL + "/api"
    SOLR_URL = LWS_URL + "/solr/" + COLLECTION
    COL_URL = API_URL + "/collections/" + COLLECTION

    solr = pysolr.Solr(SOLR_URL, timeout=10)
    app.debug = True
    app.run(host='0.0.0.0')
