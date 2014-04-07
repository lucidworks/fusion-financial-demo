#!/usr/bin/python

from lweutils import json_http, pretty_json, parse_opts



##
def get_id(opts, DS_URL):
    """
    Determines the id of the datasource the client is interested in
    either because it was explicitly mentioned, or by looking up the name.
    The 'id' key is removed from the data if present.
    The 'name' key is removed from the data if it was used to lookup the id
    """

    if 'id' in opts:
        i = str(opts['id'])
        del opts['id']
        return i

    if 'name' in opts:
        ids = []
        name = opts['name']
        del opts['name']
        data = json_http(DS_URL)
        for ds in data:
            if 'name' in ds and ds['name'] == name:
                ids.append(ds['id'])
        if 0 == len(ids):
            raise Exception("Can't locate a DataSource with name="+name)
        if 1 != len(ids):
            raise Exception("Multiple DataSource's found with name="+name+": "+str(ids))
        return str(ids.pop())

    return None

##
def print_ds(data, DS_URL, indent=''):
    i = str(data['id'])
    dsu = DS_URL + '/' + i

    print indent + "Data Source #" + i +': '
    indent = indent + '  '

    print indent + "Info: " + dsu + ' => ' + pretty_json(data, indent)

    status_url = dsu + "/status"
    status = json_http(status_url)
    print indent + "Status: " + status_url + " => " + pretty_json(status,indent)

    sched_url = dsu + "/schedule"
    sched = json_http(sched_url)
    print indent + "Schedule: " + sched_url + " => " + pretty_json(sched,indent)

##
def help(args):
    """display the list of commands"""
    print """Usage: ds.py {cmd} [k1=v1 k2=v2 ...]
 Commands...
  help     => prints this help
  show     => show datasources; takes an optional id (or name) key=val arg
  create   => create a datasource; takes key=val args
  update   => update a datasource; takes key=val args
  schedule => modify the schedule of a datasource; takes key=val args
  status   => show the status of a datasource; takes an optional id (or name) key=val arg
   history  => show the indexing history of a datasource; takes a mandatory id (or name) key=val arg
  delete   => delete a datasource; takes a mandatory id (or name) key=val arg
"""

##
def show(args, DS_URL):
    """display current datasources"""
    if 1 < len(args):
        raise Exception("wrong number of args for showing a DataSource")

    i = get_id(parse_opts(args))

    if (i is None):
        print 'Data Sources: ' + DS_URL
        data = json_http(DS_URL)
        
        if 0 == len(data):
            print '  (none)'
        else:
            for ds in data:
                print_ds(ds, '  ')
    else:
        print_ds(json_http(DS_URL + '/' + i))

##
def create(args, DS_URL, added_data=None):
    """create a datasource"""

    data = parse_opts(args)
    if 'name' not in data:
        raise Exception("Creating a DataSource requires a name")
    if 'type' not in data:
        raise Exception("Creating a DataSource requires a type")
    if 'crawler' not in data:
        raise Exception("Creating a DataSource requires a crawler")
    if added_data:
        data.update(added_data)
    rsp = json_http(DS_URL, method='POST', data=data)
    print "Created New DataSource: "+str(rsp['id'])+" with name: "+data['name'] + " at " + DS_URL
    return rsp['id']
##
def update(args, DS_URL):
    """modify properties of a datasource"""

    data = parse_opts(args)
    i = get_id(data)
    if i is None:
        raise Exception("Updating a DataSource requires either an id or a name")

    json_http(DS_URL+"/"+i, method='PUT', data=data)
    print "Updated DataSource #"+i

##
def schedule(args, DS_URL):
    """modify the schedule of a datasource"""

    data = parse_opts(args)
    i = get_id(data)
    if i is None:
        raise Exception("Modifying the schedule of a DataSource requires either an id or a name")

    json_http(DS_URL+"/"+i+'/schedule', method='PUT', data=data)
    print "Updated Schedule of DataSource #"+i

##
def status(args, DS_URL):
    """display status of datasources"""
    if 1 < len(args):
        raise Exception("wrong number of args for showing DataSource status")

    i = get_id(parse_opts(args))

    if (i is not None):
        url = DS_URL + '/' + i + '/status'
        data = json_http(url)
        print "Status of DataSource #"+i+": "+url+" => " + pretty_json(data)

    else:
        url = DS_URL + "/all/status"
        data = json_http(url)
        print "Status of All DataSources: "+url+" => " + pretty_json(data)

##
def history(args, DS_URL):
    """display the indexing history of a datasource"""

    if 1 != len(args):
        raise Exception("wrong number of args for showing a DataSource")

    i = get_id(parse_opts(args))
    if i is None:
        raise Exception("Must supply either an id or a name to view the indexing history of a DataSource")

    url = DS_URL+"/"+i+'/history'
    data = json_http(url)
    print  "History of DataSource #"+i+": "+url+" => " + pretty_json(data)


##
def delete(args, DS_URL):
    """remove a datasource"""
    
    if 1 != len(args):
        raise Exception("wrong number of args for deleting a DataSource")

    i = get_id(parse_opts(args))
    if i is None:
        raise Exception("Must supply either an id or a name for a DataSource to delete it")

    json_http(DS_URL+'/'+i, method='DELETE')
    print  "Deleted DataSource #"+i
    

