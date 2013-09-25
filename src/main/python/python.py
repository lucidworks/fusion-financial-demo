import optparse
from flask import Flask
from flask import render_template
from flask import request
import pysolr
from pysolr import Results
import math


app = Flask(__name__)


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


@app.route('/', methods=['POST', 'GET'])
def standard(name=None):
    # do a match all request
    query = "*:*"
    if request.method == 'POST' and request.form['search_box']:
        query = request.form['search_box']
    rows = 10
    if request.args.get('row'):
        rows = request.args.get('row')

    app.logger.info("Query: " + query)
    kwargs = {"qt": "/lucid", "facet": "true", "rows": rows, "fl":"*,score",
              "facet.range":["open", "close", "volume"],
              "facet.range.start":"0",
              "facet.range.end":"1000",
              "facet.range.gap":"100",
              "facet.range.other":"all",
              "facet.mincount":"0",
              "f.volume.facet.range.gap":"500000",
              "f.volume.facet.range.start":"10000",
              "f.volume.facet.range.end":"5000000",
              "facet.pivot":["open,close,volume", "attr_username,attr_retweetcount"],
              "stats":"true",
              "stats.field":["open", "close","volume"],

        }
    params = {'q': query}
    params.update(kwargs)
    solr_rsp = solr._select(params)
    result = solr.decoder.decode(solr_rsp)
    response = result.get('response') or {}
    facets = result.get('facet_counts') or {}
    stats = result.get('stats') or {}
    #app.logger.info("Facets: " + facets)
    numFound = response.get('numFound', 0)
    result_kwargs = process_solr_rsp(result)

    results = Results(response.get('docs', ()), numFound, **result_kwargs)
    page_count = int(math.ceil(numFound / 10))
    start = response.get('start')
    current_page_number = int(math.ceil(start/10))
    if page_count > 0:
        current_page_number += 1
    #page_count = (int) Math.ceil(results_found / (double) results_per_page);
    #current_page_number = (int) Math.ceil(start / (double) results_per_page) + (page_count > 0 ? 1 : 0);
    #
    #app.logger.info("Saw {0} result(s).".format(len(results)))
    return render_template('standard.html', name=name, search_results=results,
                           raw_response=response,
                           the_facets=facets,
                           the_stats=stats,
                           the_query=query, current_page=current_page_number,
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
