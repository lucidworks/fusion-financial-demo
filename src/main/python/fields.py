#!/usr/bin/python

import sys
from lweutils import json_http, pretty_json, parse_opts
import lweutils
import httplib2

import logging
import sys
import os

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class FieldsConnection:
    def __init__(self, url):
        self.url = url

    def create(self, name, indexed=True, stored=True, type="string", multi_valued=False, copy_fields=None):
        if name is None:
            raise ValueError("name can not be None")
        logger.debug("checking for field '{}'".format(name))
        HTTP_CLIENT = httplib2.Http()
        resp, content = HTTP_CLIENT.request(self.url + "/" + name, method='GET', body=None)
        if resp.status == 404:
            data = {
                "name": name,
                "type": type,
                "stored": stored,
                "indexed": indexed
            }
            if multi_valued:
                data["multiValued"]=True
            if copy_fields is not None:
                data["copyFields"] = copy_fields
            logger.info("Creating new field: {} at: {} with data: {}".format(name, self.url, data))
            rsp = json_http(self.url + "/" + name, method='PUT', data=data)

            logger.info("Created new field: {} at: {}".format(name, self.url))
        else:
            logger.info("there is an existing field '{}'".format(name))

##
def help(args):
    """display the list of commands"""
    print """Usage: fields.py {cmd} [k1=v1 k2=v2 ...]
 Commands...
  help     => prints this help
  show     => show fields; takes an optional name arg
  create   => create a field; takes key=val args
  update   => update a field; takes key=val args
  delete   => delete a field; takes a mandatory name arg
"""

##
def create(args, FIELDS_URL):
    """create a field"""

    data = parse_opts(args)
    for arg in ('name','type'):
        if arg not in data:
            raise Exception("Creating a Field requires a " + arg)

    logger.info("Creating new field: {} at: {} with data: {}".format(data['name'], FIELDS_URL, data))
    rsp = json_http(FIELDS_URL + "/" + data['name'], method='PUT', data=data)
    logger.info("Created new field: {} at: {}".format(data['name'], FIELDS_URL))

##
def show(args, FIELDS_URL):
    """display current fields"""
    if 1 < len(args):
        raise Exception("wrong number of args for showing fields")

    if (0 < len(args)): 
        name = args.pop(0)
        # be helpful if they get the syntax confused
        if (0 == name.find('name=')): name = name.replace('name=','',1)
        url = FIELDS_URL + "/" + name
        data = json_http(url)
        logger.info("Field {}: {} => {}".format(name, url, pretty_json(data, '  ')))
    else:
        logger.info('Fields: ' + FIELDS_URL)
        data = json_http(FIELDS_URL)
        if 0 == len(data):
            logger.info('  (none)')
        else:
            for field in data:
                name = field['name']
                url  = FIELDS_URL + '/' + name
                logger.info("  Field: {}: {} => {}".format(name, url, pretty_json(field, '  ')))

##
def update(args, FIELDS_URL):
    """modify properties of a Field"""

    data = parse_opts(args)
    if 'name' not in data:
        raise Exception("Updating a Field requires a name")
    name = data['name']
    del data['name']

    json_http(FIELDS_URL + "/"+name, method='PUT', data=data)
    logger.info("Updated Field: "+name)

##
def delete(args, FIELDS_URL):
    """remove a Field"""

    if 1 != len(args):
        raise Exception("Deleting a Field requires a name")

    name = args.pop(0)
    # be helpful if they get the syntax confused
    if (0 == name.find('name=')):
        name = name.replace('name=','',1)

    json_http(FIELDS_URL +"/"+name, method='DELETE')
    logger.info("Deleted Field: "+name)
