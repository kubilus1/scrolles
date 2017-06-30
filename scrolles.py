#!/usr/bin/env python

import os
import time
import json
import urllib2
import argparse

def dourl(url, method='GET', data=None):
    req = urllib2.Request(url, data)
    req.get_method = lambda: method
    h = urllib2.urlopen(req)
    return h.read()

def scrolles(url, index):
    URL="%s/%s/_search" % (url, index)
    # ElasticSearch needs some time to settle down 
    QUERY='{"range":{"@timestamp":{"lt":"now-20s"}}}'
    #QUERY='{"match_all": {}}'

    INITJSON='{"size":50, "query": %s, "sort": [{"@timestamp": "desc"}, {"_uid":"desc"}]}' % QUERY
    search_data = json.loads(dourl(URL, data=INITJSON))
    search_date = search_data.get('hits').get('hits')[-1].get('sort')[0]
    search_uid = search_data.get('hits').get('hits')[-1].get('sort')[1]
    while True:
        log_data = json.loads(dourl(
            URL,
            data = '{ "size":50, "query": %s, "search_after": [%s,"%s"], "sort": [ {"@timestamp": "asc"},{"_uid":"asc"} ] }' % (QUERY, search_date, search_uid)
        ))
        if len(log_data.get('hits').get('hits')):
            search_date = log_data.get('hits').get('hits')[-1].get('sort')[0]
            search_uid = log_data.get('hits').get('hits')[-1].get('sort')[1]
            for hit in log_data.get('hits').get('hits'):
                print hit.get('_source').get('message')
        time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    conf = {
        "index":"*",
        "url":"http://localhost:9200"
    }

    localpath = os.path.expanduser('~/.scrolles.json')
    if os.path.isfile(localpath):
        with open(localpath,'r') as h:
            conf.update(json.loads(h.read()))
    elif os.path.isfile('/etc/scrolles.json'):
        with open('/etc/scrolles.json','r') as h:
            conf.update(json.loads(h.read()))

    parser.add_argument('--url', dest="url", help="ElasticSearch URL", default=conf.get('url'))
    parser.add_argument('--index', dest="index", help="ElasticSearch Index", default=conf.get('index'))
    args = parser.parse_args()
    scrolles(args.url, args.index)
