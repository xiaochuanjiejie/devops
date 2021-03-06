#!/usr/bin/python
# coding: utf-8

import re
import time
import requests
import datetime
from elasticsearch5 import Elasticsearch

'''
SLB中域名mc-im.01zhuanche.com的500状态码速率大于5次/分
'''

TIMEFORMAT='%Y%m%d%H%M%S'
TIMEFORMAT_DAY='%Y%m%d'
start_time_t = time.time() - 60
stop_time_t  = time.time()
start_time   = time.strftime(TIMEFORMAT,time.localtime(start_time_t))
stop_time    = time.strftime(TIMEFORMAT,time.localtime(stop_time_t))
cur_day      = time.strftime(TIMEFORMAT_DAY,time.localtime(stop_time_t))
d_error = {}

def get_zabbix_alert_list(query,start_time,stop_time,get_type='default'):
    if query == 'query':
        start = datetime.datetime.strptime(start_time, '%Y%m%d%H%M%S')
        stop = datetime.datetime.strptime(stop_time, '%Y%m%d%H%M%S')
        delta = stop - start
        print delta,type(delta)
        period = int(delta.total_seconds())
        ur = "&period=%s&stime=%s" % (period,start_time)
    else:
        period = int(query)
        ur = "&period=%s" % period

    cookies = dict(cookies_are='PHPSESSID=23lchar0js2mq86lpr0or6r191; tab=0; zbx_sessionid=ed0072d0e6101bea08d8eef995ea1c50')
    r = requests.get('http://zabbix.01zhuanche.com/zabbix/zabbix.php?action=problem.view.csv&page=1%s' % ur,cookies=cookies)
    # r.text(unicode)  r.content(str)
    # searchObj = re.search(r'SLB中域名(.*)次/分', r.content, re.M | re.I | re.S)
    # print "searchObj.group() : ", searchObj.group()
    info = r.content.split("\n")
    for line in info:
        searchObj = re.search(r'SLB中域名(.*)的(.*)状态码速率大于(.*)次/分', line, re.M | re.I | re.S)
        if searchObj:
            # print "searchObj.group() : ", searchObj.group()
            # print "searchObj.group(1) : ", searchObj.group(1)
            # print "searchObj.group(2) : ", searchObj.group(2)
            # print "searchObj.group(3) : ", searchObj.group(3)
            d_error[searchObj.group(1)] = searchObj.group(2)
        else:
            print 'Nothing found!'

get_zabbix_alert_list('query',start_time,stop_time)

idx_name = 'logstash-slb_%s' % cur_day
def find_es(idx_name,domain,status):
    body = {
        "query" : {
            "bool" : {
                "filter" : {
                    "range" : {
                        "@timestamp" : { "gt" : 'now-2m' }
                    }
                },
                "must" : [
                    # {"match":{"http_host" : "flight.01zhuanche.com"}},
                    # {"match":{"status":"404"}}
                    {"match": {"http_host": domain}},
                    {"match": {"status": status}}
                ]
            }
        }
    }

    es = Elasticsearch(hosts='http://10.66.5.28:9200', timeout=300)
    Es_Data = es.search(index='%s' % idx_name, body=body)
    print Es_Data
    print Es_Data["hits"]["hits"][0]['_source']['remote_addr']

if d_error:
    for item in d_error:
        print item,'--',d_error[item]
        if d_error[item] == 400 or d_error[item] == 403 or d_error[item] == 404 or d_error[item] == 500:
            find_es(idx_name,item,d_error[item])
        else:
            print '需人工检查域名对应业务情况'
else:
    print '无域名有400、403、404、500异常'


# d_error = {}
# def get_zabbix_alert_list(query,start_time,stop_time,get_type='default'):
#     if query == 'query':
#         start = datetime.datetime.strptime(start_time, '%Y%m%d%H%M%S')
#         stop = datetime.datetime.strptime(stop_time, '%Y%m%d%H%M%S')
#         delta = stop - start
#         period = int(delta.total_seconds())
#         ur = "&period=%s&stime=%s" % (period,start_time)
#     else:
#         period = int(query)
#         ur = "&period=%s" % period
#
#     cookies = dict(cookies_are='PHPSESSID=23lchar0js2mq86lpr0or6r191; tab=0; zbx_sessionid=ed0072d0e6101bea08d8eef995ea1c50')
#     r = requests.get('http://zabbix.01zhuanche.com/zabbix/zabbix.php?action=problem.view.csv&page=1%s' % ur,cookies=cookies)
#     # r.text(unicode)  r.content(str)
#     # searchObj = re.search(r'SLB中域名(.*)次/分', r.content, re.M | re.I | re.S)
#     # print "searchObj.group() : ", searchObj.group()
#     info = r.content.split("\n")
#     for line in info:
#         searchObj = re.search(r'SLB中域名(.*)的(.*)状态码速率大于(.*)次/分', line, re.M | re.I | re.S)
#         if searchObj:
#             print "searchObj.group() : ", searchObj.group()
#             print "searchObj.group(1) : ", searchObj.group(1)
#             print "searchObj.group(2) : ", searchObj.group(2)
#             print "searchObj.group(3) : ", searchObj.group(3)
#             d_error[searchObj.group(1)] = searchObj.group(2)
#         else:
#             print 'Nothing found!'
#
# get_zabbix_alert_list('query','20200213143000','20200213150000')
#
# idx_name = 'logstash-slb_20200217'
# body = {
#     "query" : {
#         "bool" : {
#             "filter" : {
#                 "range" : {
#                     "@timestamp" : { "gt" : 'now-5m' }
#                 }
#             },
#             "must" : {
#                 "match" : {
#                     "http_host" : "www.01zhuanche.com"
#                 }
#             }
#         }
#     }
# }
#
# es = Elasticsearch(hosts='http://10.66.5.28:9200', timeout=300)
# Es_Data = es.search(index='%s' % idx_name, body=body)
# # print Es_Data
# print Es_Data["hits"]["hits"][0]['_source']['remote_addr']