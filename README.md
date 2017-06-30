# ScrollES
Yet another tail ElasticSearch/ELK logs program.

The purpose of this project is to provide a tail-like experience to parse ELK
logs.  Projects such as elktail seem to no longer support newer version of
ElastiSearch.

There are several examples of using ElasticSearch 'scroll' feature, but as
stated in the ES documentation that such an approach is heavy-weight and not
intended for real-time requests.

ScrollES, OTOH, uses the 'search_after' feature of ES and is therefore lower
impact.

NOTE: Tailing ElasticSearch is tricky in real time since all of the latest
documents may not have settled by the time you query.  The net-effect is that
it is possible to have missing lines in the output.  I have attempted to
mitigate that as much as possible by returning data that is at least 20
seconds old.

## Usage

```
$ scrolles.py --url <elasticsearch url> --index <elasticsearch index>
```

## Configuration

You can set default configuration by specifying the arguments in JSON.  For
example:

```
{
    "url": "http://192.168.1.1:9200"
    "index": "logstash-*"
}
```

Configuration is searched first in ~/.scrolles.json, then at
/etc/scrolles.json

You can override configuration by specifying parameters at the command line.

## TODOs

* Add search parameters
* Add tag searching
