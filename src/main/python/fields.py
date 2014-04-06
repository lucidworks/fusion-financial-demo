#!/usr/bin/python

import sys
from lweutils import json_http, pretty_json, parse_opts
import lweutils


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
    for arg in ('name','field_type'):
        if arg not in data:
            raise Exception("Creating a Field requires a " + arg)

    rsp = json_http(FIELDS_URL, method='POST', data=data)
    print "Created New Field: "+data['name'] + " at: " + FIELDS_URL

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
        print "Field "+name+": "+url+" => "+pretty_json(data, '  ')
    else:
        print 'Fields: ' + FIELDS_URL
        data = json_http(FIELDS_URL)
        if 0 == len(data):
            print '  (none)'
        else:
            for field in data:
                name = field['name']
                url  = FIELDS_URL + '/' + name
                print "  Field: "+name+": "+url+" => " + pretty_json(field, '  ')

##
def update(args, FIELDS_URL):
    """modify properties of a Field"""

    data = parse_opts(args)
    if 'name' not in data:
        raise Exception("Updating a Field requires a name")
    name = data['name']
    del data['name']

    json_http(FIELDS_URL + "/"+name, method='PUT', data=data)
    print "Updated Field: "+name

##
def delete(args, FIELDS_URL):
    """remove a Field"""

    if 1 != len(args):
        raise Exception("Deleting a Field requires a name")

    name = args.pop(0)
    # be helpful if they get the syntax confused
    if (0 == name.find('name=')): name = name.replace('name=','',1)

    json_http(FIELDS_URL +"/"+name, method='DELETE')
    print "Deleted Field: "+name
