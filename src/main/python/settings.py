#!/usr/bin/python

import sys
from lweutils import COL_URL, json_http, pretty_json, parse_opts

SETTINGS_URL = COL_URL + '/settings'

##
def help(args):
    """display the list of commands"""
    print """Usage: settings.py {cmd} [k1[=v1] k2[=v2] ...]
 Commands...
  help     => prints this help
  show     => show settings; takes an optional list of setting names
  update   => update some settings; takes key=val args
"""

##
def show(args):
    """display settings """

    label = 'Index Settings'
    url = SETTINGS_URL
    if (0 < len(args)): 
        label += ' (' + ', '.join(args) + ')'
        url += '/' + ','.join(args)
    data = json_http(url)
    print label + ': ' + url + ' => ' + pretty_json(data)

##
def update(args):
    """modify settings"""

    data = parse_opts(args)
    json_http(SETTINGS_URL, method='PUT', data=data)
    print "Updated Settings"


ACTIONS = {
    'help' : help,
    'show' : show,
    'update' : update,
}

#########################################


# toss the program name
sys.argv.pop(0)

action = 'help'
if 0 < len(sys.argv): action = sys.argv.pop(0).lower()

if action in ACTIONS: 
    ACTIONS[action](sys.argv)
else:
    raise Exception(action+" is not a valid action")

