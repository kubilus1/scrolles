#!/usr/bin/env python

import os
import time
import json
import urllib
import urllib2
import argparse

def dourl(url, method='GET', data=None, timeout=30):
    req = urllib2.Request(url, data)
    req.get_method = lambda: method
    h = urllib2.urlopen(req, timeout=timeout)
    return h.read()

def scrolles(url, index, numlines=50, keys=None, search=None):
    if search:
        URL="%s/%s/_search?q=%s" % (url, index, urllib.quote(search))
    else:
        URL="%s/%s/_search" % (url, index)
    # ElasticSearch needs some time to settle down 
    QUERY='{"range":{"@timestamp":{"lt":"now-20s"}}}'

    INITJSON='{"size":%s, "query": %s, "sort": [{"@timestamp": "desc"}, {"_uid":"desc"}]}' % (numlines, QUERY)
    search_data = json.loads(dourl(URL, data=INITJSON, timeout=120))
    search_date = search_data.get('hits').get('hits')[-1].get('sort')[0]
    search_uid = search_data.get('hits').get('hits')[-1].get('sort')[1]
    while True:
        try:
            log_data = json.loads(dourl(
                URL,
                data = '{ "size":%s, "query": %s, "search_after": [%s,"%s"], "sort": [ {"@timestamp": "asc"},{"_uid":"asc"} ] }' % (numlines, QUERY, search_date, search_uid)
            ))
        except Exception, err:
            print "ScrollES Error", err
            continue

        if len(log_data.get('hits').get('hits')):
            search_date = log_data.get('hits').get('hits')[-1].get('sort')[0]
            search_uid = log_data.get('hits').get('hits')[-1].get('sort')[1]
            for hit in log_data.get('hits').get('hits'):
                try:
                    source_data = hit.get('_source')
                    for k in keys:
                        print source_data.get(k),
                    print
                except Exception, err:
                    print "ERR", err
                    return

        time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    conf = {
        "index":"*",
        "url":"http://localhost:9200",
        "key":["message"],
        "numlines":50,
        "search":None
    }

    localpath = os.path.expanduser('~/.scrolles.json')
    if os.path.isfile(localpath):
        with open(localpath,'r') as h:
            conf.update(json.loads(h.read()))
    elif os.path.isfile('/etc/scrolles.json'):
        with open('/etc/scrolles.json','r') as h:
            conf.update(json.loads(h.read()))

    parser.add_argument('-u','--url', dest="url", help="ElasticSearch URL", default=conf.get('url'))
    parser.add_argument('-i','--index', dest="index", help="ElasticSearch Index", default=conf.get('index'))
    parser.add_argument('-k','--key', action="append", help="Keys to display")
    parser.add_argument('-s','--search', dest="search", help="Search string", default=conf.get('search'))
    parser.add_argument('-n','--numlines', type=int, dest="numlines", help="Initial number of lines to show from the logs", default=conf.get('numlines'))
    args = parser.parse_args()

    key = args.key
    if not key:
        key = conf.get('key')

    scrolles(args.url, args.index, args.numlines, key, args.search)
