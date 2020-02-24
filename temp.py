#!/usr/bin/python
# coding: utf-8

import re
import time
import requests
import datetime
from elasticsearch5 import Elasticsearch

# idx_name = 'logstash-slb_%s' % cur_day
# def find_es(idx_name,domain,status):
#     body = {
#         "query" : {
#             "bool" : {
#                 "filter" : {
#                     "range" : {
#                         "@timestamp" : { "gt" : 'now-2m' }
#                     }
#                 },
#                 "must" : [
#                     # {"match":{"http_host" : "flight.01zhuanche.com"}},
#                     # {"match":{"status":"404"}}
#                     {"match": {"http_host": domain}},
#                     {"match": {"status": status}}
#                 ]
#             }
#         }
#     }
#
#     es = Elasticsearch(hosts='http://10.66.5.28:9200', timeout=300)
#     Es_Data = es.search(index='%s' % idx_name, body=body)
#     print Es_Data
#     print Es_Data["hits"]["hits"][0]['_source']['remote_addr']
#
# if d_error:
#     for item in d_error:
#         print item,'--',d_error[item]
#         if int(d_error[item]) == 400 or int(d_error[item]) == 403 or int(d_error[item]) == 404 or int(d_error[item]) == 500:
#             find_es(idx_name,item,d_error[item])
#         else:
#             print '需人工检查域名对应业务情况'
# else:
#     print '无域名有400、403、404、500异常'

stime = int(round(time.time() - 120) * 1000)
dtime = int(round(time.time() - 60) * 1000)
print 'stime: %s,dtime: %s' % (stime,dtime)

def Get_Error(stime,dtime,idx_name,domain,status):
    # body = {
    #   "size": 10000,
    #   "sort": {
    #     "@timestamp": {
    #       "order": "desc",
    #       "unmapped_type": "boolean"
    #     }
    #   },
    #   "_source": {
    #     "excludes": []
    #   },
    #   "stored_fields": ["*"],
    #   "docvalue_fields": ["@timestamp"],
    #   "query" : {
    #     "constant_score" : {
    #       "filter" : {
    #           "bool": {
    #               # "must": {"exists": {"field": "%s" % field_name}},
    #               # "must_not": {"term": {"%s.keyword" % field_name: ""}},
    #               {"match": {"http_host": domain}},
    #               {"match": {"status": status}},
    #               "must": {"range":{"@timestamp":{"gte":stime,"lte":dtime}}}
    #           }
    #       }
    #     }
    #   }
    # }
    body = {
        "size": 10000,
        "query" : {
            "bool" : {
                "filter" : {
                    "range" : {
                        "@timestamp" : {"gte":stime,"lte":dtime}
                    }
                },
                "must" : [
                    # {"match":{"http_host" : "flight.01zhuanche.com"}},
                    # {"match":{"status":"404"}}
                    {"match_phrase": {"http_host": domain}},
                    {"match": {"status": status}}
                ]
            }
        }
}
    es = Elasticsearch(hosts='http://10.66.5.28:9200', timeout=300)
    Es_Data = es.search(index='%s' % idx_name, body=body)
    print Es_Data

if __name__ == "__main__":
    # stime: 1582189812000, dtime: 1582189872000
    # stime: 1582101481000, dtime: 1582101541000
    # start_time: 20200219163801, stop_time: 20200219163901
    # Get_Error(1582101301000,1582101781000,'logstash-slb_20200219','m.01zhuanche.com','400')
    Get_Error(1582101360000, 1582101541000, 'logstash-slb_20200219', 'm.01zhuanche.com', '400')