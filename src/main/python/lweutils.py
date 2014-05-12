
import os
import json
import httplib2

import logging
import sys
import time

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

HTTP_CLIENT = httplib2.Http()

##
def get_env(key, default=None):
    if key in os.environ:
        return os.environ[key]
    return default

##
def parse_opts(args):
    data = {}
    for arg in args:
        key, val = arg.split('=', 1)

        # make a list out of any key specified more then once
        if key in data:
            oldval = data[key]
            if type(oldval) is list:
                oldval.append(val)
            else:
                data[key] = [oldval, val]
        else:
            data[key] = val
    return data


##
def json_http(url, method='GET', data=None):
    body = None;
    if (data): body = json.dumps(data)

    logger.debug("json_http method={} url={} data={}".format(method, url, data))
    resp, content = HTTP_CLIENT.request(
        url, method=method, body=body, 
        headers={'Content-Type':'application/json'})
    logger.debug("json_http resp={} content={}".format(resp, content))

    # fail if not status 2xx
    if 0 != str(resp.status).find('2'):
        err = content
        try:
            err = pretty_json(json.loads(content))
        except:
            # IGNORE, use the raw error instead
            pass
        raise Exception(method+' '+url+' => '+str(resp.status)+"\n"+err)

    if 204 == resp.status: return None
    if content:
        return json.loads(content)
    else:
        return None

##
def pretty_json(data, indent=''):
    pretty = json.dumps(data,indent=2)
    return pretty.replace("\n","\n"+indent)

##
def sleep_secs(secs, message=""):
    logger.debug("sleeping {} secs {}".format(secs, message))
    time.sleep(secs)
    logger.debug("woken up")

