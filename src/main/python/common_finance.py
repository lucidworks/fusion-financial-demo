import optparse
import urllib2
import time
import datetime

import pysolr
import common_finance

import ds
import fields
import traceback
try:
    # Prefer lxml, if installed.
    from lxml import etree as ET
except ImportError:
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        raise ImportError("No suitable ElementTree implementation was found.")

import lweutils



def load_stocks(file):
    stocks = {}
    for line in file:
        if line.startswith("#") == False:
            vals = line.split(",")
            symbol = vals[0]
            stocks[symbol] = vals
    return stocks

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
    #print "Indexing to: " + dsId
    end_time = time.time()
    #self.log.debug("Built add request of %s docs in %0.2f seconds.", len(message), end_time - start_time)
    return update(solr, m, dsId, commit=commit, waitFlush=waitFlush, waitSearcher=waitSearcher)


# TODO: change me to use the indexing pipeline.
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
        #query_vars.append("fm.ds=" + dsId)
    if query_vars:
        path = '%s?%s' % (path, '&'.join(query_vars))

    # Clean the message of ctrl characters.
    if clean_ctrl_chars:
        message = pysolr.sanitize(message)

    return solr._send_request('post', path, message, {'Content-type': 'text/xml; charset=utf-8'})