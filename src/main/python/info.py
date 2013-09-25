#!/usr/bin/python

import sys
from lweutils import COL_URL, json_http, pretty_json, parse_opts

##
def help(args):
    """display the list of commands"""
    print """Usage: info.py {cmd} [k1 k2 ...]
  help   => prints this help
  show   => show collection info; takes an optional list of info keys
"""

##
def show(args):
    """display current collection info"""

    label = 'Collection Info'
    url = COL_URL + "/info"
    if (0 < len(args)): 
        label += ' (' + ', '.join(args) + ')'
        url += '/' + ','.join(args)
    data = json_http(url)
    print label+": "+url+" => "+pretty_json(data)


ACTIONS = {
    'help' : help,
    'show' : show,
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

