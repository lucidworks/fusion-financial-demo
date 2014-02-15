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
import ldap
import traceback
import sys
import lweutils
import ds
import fields

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
#path=/select params={hl.fragsize=250&echoParams=all&start=0&q=symbol:AAPL&facet.limit=11&forceElevation=true&role=user10&req_type=main
# &hl.simple.pre=LUCIDWORKS_HIGHLIGHT_START&hl.simple.post=LUCIDWORKS_HIGHLIGHT_END&json.nl=map&user=user.10&qt=/lucid&wt=ruby&rows=10} hits=0 status=0 QTime=10
@app.route('/', methods=['POST', 'GET'])
def standard(name=None):
    # do a match all request
    query = "*:*"
    start = 0
    user = None
    if request.method == 'POST' and request.form['search_box']:
        query = request.form['search_box']

    else:
        if request.args.get('q'):
            query = request.args.get('q')

    if request.method == 'POST' and request.form['user']:
        user = request.form['user']
    else:
        if request.args.get('user'):
            user = request.args.get('user')
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
    kwargs = {"qt": "/lucid", "facet": "true", "start": start, "fl": "*,score", "facet.date": "timestamp",
              "facet.date.start": "NOW/DAY-30DAY", "facet.date.end": "NOW/DAY+1DAY", "facet.date.gap": "+1DAY",
              "facet.date.other": "all", "facet.range": ["open", "close", "volume"], "facet.range.start": "0",
              "facet.range.end": "1000", "facet.range.gap": "100", "facet.range.other": "all", "facet.mincount": "1",
              "f.open.facet.limit": "5", "f.close.facet.limit": "5", "f.close.open.limit": "5",
              "f.volume.facet.limit": "5", "f.volume.facet.range.gap": "500000", "f.volume.facet.range.start": "10000",
              "f.volume.facet.range.end": "5000000",
              "facet.pivot": ["open,close,volume", "attr_retweetcount,attr_username"], "sort": "timestamp desc",
              "stats": "true", "group": group, "group.field": group_field, "group.limit": 10,
              "group.sort": "trade_date desc", "stats.field": ["open", "close", "volume"], "fq": source_filters
    }

    if fq:
        kwargs['fq'] = fq
    #the_role = "DEFAULT"

    if user and user != 'none':
        kwargs['user'] = user
        # we have a user, let's see what roles they play
        #/api/collections/collection/roles/role
        print "User: " + user
        roles = lweutils.json_http(lweutils.COL_URL + "/roles", method="GET")
        #{u'groups': [], u'users': [u'admin'], u'filters': [u'*:*'], u'name': u'DEFAULT'}
        #{u'groups': [], u'users': [u'user.10'], u'filters': [u'symbol:AES'], u'name': u'user10'}
        for role in roles:
            #print user + ", " + role['users'][0]
            for role_user in role['users']:
                if user == role_user:
                    #print role['name']
                    kwargs['role'] = role['name']  #TODO: Handle multiple roles?

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
                           the_user=user,
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
                           the_page_count=page_count,
                           users=users)


def load_users(baseDN="ou=People,dc=grantingersoll,dc=com"):
    print "Loading Users from LDAP: " + baseDN
    searchScope = ldap.SCOPE_SUBTREE
    ## retrieve all attributes - again adjust to your needs - see documentation for more options
    retrieveAttributes = None
    searchFilter = "uid=*user*"

    try:
        ldap_result_id = the_ldap.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        result_set = []
        while 1:
            result_type, result_data = the_ldap.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                ## here you don't have to append to a list
                ## you could do whatever you want with the individual entry
                ## The appending to list is just for illustration.
                if result_type == ldap.RES_SEARCH_ENTRY:
                    #print "Data: " + result_data
                    #('uid=user.49,ou=People,dc=grantingersoll,dc=com', {'telephoneNumber': ['+1 967 850 8431'],
                    #  'cn': ['Adelheid Acs'], 'uid': ['user.49'], 'objectClass': ['person', 'inetorgperson', 'organizationalperson', 'top'],
                    #  'description': ['This is the description for Adelheid Acs.'], 'sn': ['Acs'], 'l': ['New Haven'], 'st': ['AK'],
                    # 'mobile': ['+1 290 471 4170'], 'street': ['02830 Laurel Street'], 'employeeNumber': ['49'],
                    # 'postalCode': ['23905'], 'mail': ['user.49@maildomain.net'], 'postalAddress': ['Adelheid Acs$02830 Laurel Street$New Haven, AK  23905'],
                    # 'givenName': ['Adelheid'], 'pager': ['+1 417 307 3862'], 'homePhone': ['+1 006 255 9283'], 'initials': ['ABA']})
                    #print "id: " + result_data[0][0] + " val: " + result_data[0][1]["uid"][0]
                    user = {"id" : result_data[0][0], "uid": result_data[0][1]["uid"][0], "given_name": result_data[0][1]["givenName"][0]}
                    result_set.append(user)
        #print result_set
        return result_set
    except ldap.LDAPError, e:
        print "Error:"
        print e
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** print_tb:"
        traceback.print_tb(exc_traceback)


def create_filters(filters, users):
    #roles = lweutils.json_http(lweutils.COL_URL + "/roles", method="GET")
    #for role in roles:
    #    print role

    #{u'groups': [], u'users': [u'admin'], u'filters': [u'*:*'], u'name': u'DEFAULT'}
    #{u'groups': [], u'users': [u'user.10'], u'filters': [u'symbol:AES'], u'name': u'user10'}
    filters_split = filters.split(";")
    for the_filter in filters_split:
        print "Applying filter: " + the_filter
        splits = the_filter.split("=")
        #curl -H 'Content-type: application/json'
        # -d '{"name": "ONLY_PUBLIC","groups": ["group1","group2"],"filters": ["status:public"],
        # "users": ["user1"]}' http://localhost:8888/api/collections/collection1/roles
        # rolename=uids=query;uids=query
        the_users = []
        uids = splits[1].split(",")
        for uid in uids:
            the_users.append(uid)
        data = {"name": splits[0], "users": the_users, "filters": splits[2]}
        print "Sending Data to:" + lweutils.COL_URL + "/roles"
        print data
        result = lweutils.json_http(lweutils.COL_URL + "/roles", method="POST", data=data)
        print "Result:"
        print result


if __name__ == '__main__':
    p = optparse.OptionParser()
    p.add_option("--api_host", action="store", dest="host", default="localhost")
    p.add_option("-l", "--collection", action="store", dest="collection") #create the collection
    p.add_option("--api_port", action="store", dest="api_port", default="8888")
    p.add_option("--ui_host", action="store", dest="ui_host", default="localhost")
    p.add_option("--ldap", action="store", dest="ldap")#Most people are on 389
    p.add_option("--ldapuser", action="store", dest="ldap_user", default="cn=Directory Manager,cn=Root DNs,cn=config")
    p.add_option("--ldappass", action="store", dest="ldap_pass", default="abc")
    p.add_option("--create_filters", action="store", dest="create_filters")
    p.add_option("--baseDN", action="store", dest="base_dn", default="ou=People,dc=grantingersoll,dc=com")
    p.add_option("--ui_port", action="store", dest="ui_port", default="8989")
    opts, args = p.parse_args()
    COLLECTION = opts.collection
    if COLLECTION is None:
        COLLECTION = "Finance"


    LWS_URL = "http://" + opts.host + ":" + opts.api_port
    API_URL = LWS_URL + "/api"
    SOLR_URL = LWS_URL + "/solr/" + COLLECTION
    COL_URL = API_URL + "/collections/" + COLLECTION
    lweutils.COLLECTION = COLLECTION
    lweutils.LWS_URL = LWS_URL
    lweutils.API_URL = API_URL
    lweutils.SOLR_URL = SOLR_URL
    lweutils.COL_URL = COL_URL
    fields.FIELDS_URL = lweutils.COL_URL + '/fields'  #TODO: fix this
    ds.DS_URL = lweutils.COL_URL + '/datasources'
    print "Coll: " + COLLECTION
    print " lweutils: " + lweutils.COLLECTION
    if (opts.ui_host and opts.ui_port):
        lweutils.UI_URL = "http://" + opts.ui_host + ":" + opts.ui_port
    else:
        lweutils.UI_URL = "http://" + opts.host + ":8989"
    lweutils.UI_API_URL = lweutils.UI_URL + "/api"

    users = {}
    if opts.ldap:
        try:
            print "Initializing LDAP"
            the_ldap = ldap.initialize(opts.ldap)
            #the_ldap.simple_bind(opts.ldap_user, opts.ldap_pass)
            users = load_users(opts.base_dn)
            if opts.create_filters:
                create_filters(opts.create_filters, users)
                
        except ldap.LDAPError, e:
            print e
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "*** init error:"
            traceback.print_tb(exc_traceback)



    solr = pysolr.Solr(SOLR_URL, timeout=10)
    app.debug = True
    app.run(host='0.0.0.0')
