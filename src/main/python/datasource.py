
import argparse
import json
import logging
import pprint
import sys
import httplib2

from lweutils import json_http, pretty_json, sleep_secs


logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logger = logging.getLogger()

class DataSourceConnection:

    def __init__(self, connectors_url):
        """
        Create a datasource connection.
        The url passed should point to the connectors API, e.g.:
        http://localhost:8984/connectors/api/v1/connectors
        """
        self.connectors_url = connectors_url
        self.datasources_url = self.connectors_url + "/datasources"
        self.jobs_url = self.connectors_url + "/jobs"

    def datasources(self):
        """lookup datasources, and return a dictionary of id->DataSource objects."""
        logger.debug("requesting {}".format(self.datasources_url))
        result=json_http(self.datasources_url)
        logger.debug("got: {}".format(result))
        if result is None:
            raise ValueError("failed to get datasources")
        data_sources = {}
        for ds in result:
            data_sources[ds['id']] = DataSource(self, ds)
        return data_sources

    def get(self, datasource_id):
        """lookup a specific data source by id."""
        for ds_id, ds in self.datasources().iteritems():
            if datasource_id == ds_id:
                return ds
        return None

    def _datasource_http(self, data, method='POST'):
        # HACK: the connectors API doesn't return JSON for this call, but a bare datasource id.
        # So we can't use json_http, and call by hand.
        # This is fixed in https://github.com/LucidWorks/connectors/commit/a665278b777e9d3886a242d459f21f55cea1a97d
        url=self.datasources_url
        logger.info("Creating New DataSource: {} to {}: {}".format(method, url, data))
        http = httplib2.Http()
        resp, content = http.request(url, method=method, body=json.dumps(data),
            headers={'Content-Type':'application/json'})
        logger.debug("response: {}".format(resp))
        if 0 != str(resp.status).find('2'):
            err = content
            try:
                err = pretty_json(json.loads(content))
            except:
                # IGNORE, use the raw error instead
                pass
            message = "{} {} => {}\n{}".format(method, url, resp.status, err)
            raise Exception(message)
        if len(content) > 1 and content[0] == '[':
            # Oh, we did get json. See comment above
            logger.error("FIX _datasource_http to use json_http instead of calling by hand")
            datasource_data = json.loads(content)
            datasource_id = datasource_data['id']
        else:
            datasource_id = content
        logger.info("Created New DataSource: {}".format(datasource_id))
        sleep_secs(5, "waiting for the datasource to get created")
        datasource = self.get(datasource_id)
        if datasource is None:
            raise ValueError("cannot find datasource {} even though it was created")
        logger.debug("datasource created: {}".format(datasource))
        return datasource

    def create_web(self, name=None, pipeline="conn_solr", depth=0, connector="lucid.anda", start_urls=None, restrictToTree=False, include_regexps=None):
        """create a web datasource."""
        if start_urls is None:
            raise ValueError("start_urls must not be None")
        found = self.get(name)
        if found is not None:
            logger.debug("connector {} already exists".format(name))
            return found
        data = {
            'id': name,
            'connector': connector,
            'type': 'web',
            'pipeline': pipeline,
            'properties': {
                'c.startURIs': start_urls,
                'c.depth': depth,
                'c.restrictToTree': restrictToTree,
            }
        }
        if include_regexps is not None:
            data['properties']['c.includeRegexes'] = include_regexps

        return self._datasource_http(data)

    def create_push(self, name=None, pipeline="conn_solr", port=0, data=None):
        if port == 0:
            raise ValueError("port cannot be 0")
        found = self.get(name)
        if found is not None:
            logger.debug("connector {} already exists", name)
            return found
        data = {
            'id': name,
            'connector': "lucid.push",
            'type': 'push',
            'pipeline': pipeline,
            'properties': {
                'port': port
            }
        }
        return self._datasource_http(data)

    def create_twitter(self, name=None, pipeline="conn_solr", access_token=None, consumer_key=None, consumer_secret=None,
        token_secret=None, sleep=10000, data=None):
        """create a twitter datasource."""
        if name is None:
            raise ValueError("name must not be None")
        if access_token is None:
            raise ValueError("access_token must not be None")
        if consumer_key is None:
            raise ValueError("consumer_key must not be None")
        if consumer_secret is None:
            raise ValueError("consumer_secret must not be None")
        if token_secret is None:
            raise ValueError("token_secret must not be None")
        found = self.get(name)
        if found is not None:
            logger.debug("connector {} already exists".format(name))
            return found
        data = {
            "id": name,
            'connector': "lucid.twitter.stream",
            'type': 'twitter_stream',
            'pipeline': pipeline,
            'properties': {
                "access_token": access_token, 
                "consumer_key": consumer_key,
                "consumer_secret": consumer_secret,
                "token_secret": token_secret
            }
        }

        return self._datasource_http(data)

    def get_connectors_url(self):
        return self.connectors_url

    def get_datasources_url(self):
        return self.datasources_url

    def get_jobs_url(self):
        return self.jobs_url


class DataSource:

    def __init__(self, connection, data):
        self.connection = connection
        self.data = data

    def my_url(self):
        return "{}/{}".format(self.connection.get_datasources_url(), self.datasource_id())

    def datasource_id(self):
        return self.data['id']

    def db(self):
        return json_http("{}/db".format(self.my_url()))

    def is_running(self):
        result = json_http("{}/{}".format(self.connection.get_jobs_url(), self.datasource_id()), method='GET')
        if result is not None:
            logger.debug("job status: {}".format(result))
            if 'running' in result and result['running']:
                return True
        return False

    def start(self):
        if self.is_running():
            logger.info("job {} already running".format(self.datasource_id))
            return
        logger.debug("starting job {}".format(self.datasource_id))
        json_http("{}/{}".format(self.connection.get_jobs_url(), self.datasource_id()), method='POST')
        sleep_secs(5, "waiting for the datasource to get started")

    def stop(self):
        if not self.is_running():
            logger.info("job {} not running".format(self.datasource_id))
            return
        logger.debug("stopping job {}".format(self.datasource_id))
        json_http("{}/{}".format(self.connection.get_jobs_url(), self.datasource_id()), method='DELETE')
        sleep_secs(5, "waiting for the datasource to stop")

    def dump(self):
        print "Data Source #{}: ".format(self.datasource_id())
        print "Info: {}: ".format(pprint.pformat(self.data, 2))
        print "DB: {}: ".format(pprint.pformat(self.db(), 2))

    def delete(self):
        self.stop()
        print "deleting dataSource: DELETE to {}".format(self.my_url())
        response = json_http(self.my_url(), method='DELETE')
        print "deleted dataSource"

#### TODO: update, schedule, status, history

class DataSourcesCommand:
    """Process commands from the command-line."""
    def __init__(self, url):
       self.url = url
       self.connection = DataSourceConnection(url)

    def show(self, datasource_id):
        ds = self.connection.get(datasource_id)
        if ds is not None:
            ds.dump()

    def list(self):
        logger.debug("list")
        datasources=self.connection.datasources()
        for ds_id, ds in self.connection.datasources().iteritems():
            print "{}: {}".format(ds_id, ds.data)

    def delete(self, datasource_id=None):
        logger.debug("delete")
        ds = self.connection.get(datasource_id)
        if ds is not None:
            ds.delete()

    def create_web(self, pipeline="conn_solr", depth=0, connector="lucid.anda",
                   start_urls=None, restrictToTree=False, include_regexps=None):
        self.connection.create_web(connector=connector, pipeline=pipeline,
                                   start_urls=start_urls, depth=depth, restrictToTree=restrictToTree,
                                   include_regexps=include_regexps)

def main():
    logger.debug("configuring command line arguments")
    parser = argparse.ArgumentParser(description='Administer datasources.')
    parser.add_argument('--host', dest='host', action='store', default='localhost',
                    help='The connectors host (default: localhost)')
    parser.add_argument('--port', dest='port', action='store', default='8984',
                    help='The connectors port (default: 8984)')
    parser.add_argument('--debug', dest='debug', type=bool, default=False,
                    help='debug mode')

    subparsers = parser.add_subparsers(dest="which_parser")

    parser_list = subparsers.add_parser('list', help='list datasources')

    parser_show = subparsers.add_parser('show', help='show a datasource by id')
    parser_show.add_argument('datasource_id', help='the datasource id')

    parser_create = subparsers.add_parser('create_web', help='create a web datasource')
    parser_create.add_argument('--connector', help='the connector', default="lucid.anda")
    parser_create.add_argument('--pipeline', help="the pipeline", default="conn_solr")
    parser_create.add_argument('--start-url', dest="start_urls", help='start URL', action="append", required=True)
    parser_create.add_argument('--depth', type=int, help='depth to crawl', default=2)
    parser_create.add_argument('--restrictToTree', type=bool, help='restrict to tree', default=True)
    parser_create.add_argument('--include-regexp', dest="include_regexps", help='include regexps', action="append")

    parser_delete = subparsers.add_parser('delete', help='delete a datasource')
    parser_delete.add_argument('datasource_id', help='the datasource id')

    logger.debug("parsing command line arguments")
    args = parser.parse_args()
    logger.debug("parsed command line arguments: {}".format(args))

    if args.debug:
        logger.setLevel(logging.DEBUG)

    url="http://{}:{}/connectors/api/v1/connectors/datasources".format(args.host, args.port)
    logger.info("url={}".format(url))

    common_arg_names = ['host', 'port', 'func', 'which_parser', 'debug']
    sub_args = { key: vars(args)[key] for key in vars(args) if not key in common_arg_names }
    command = DataSourcesCommand(url)

    logger.debug("calling {} with arguments {}".format(args.which_parser, sub_args))
    getattr(command, args.which_parser)(**sub_args)

if __name__ == "__main__":
    main()
