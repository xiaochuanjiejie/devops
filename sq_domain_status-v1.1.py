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
# SH TIME
# cur_day      = time.strftime(TIMEFORMAT_DAY,time.localtime(stop_time_t))
cur_day	     = str(datetime.datetime.utcnow()).split()[0].replace('-','')
d_error = {}
str_addr_uri,str1,str_srv_name = '','',''
l_addr_uri,l_readdr = [],[]
d_addr_uri,d_readdr = {},{}
print 'start_time: %s ,stop_time: %s' % (start_time,stop_time)

def get_zabbix_alert_list(query,start_time,stop_time,get_type='default'):
    if query == 'query':
        start = datetime.datetime.strptime(start_time, '%Y%m%d%H%M%S')
        stop = datetime.datetime.strptime(stop_time, '%Y%m%d%H%M%S')
        delta = stop - start
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
    print 'zabbix info: %s' % str(info).decode("string_escape")
    for line in info:
        print 'line: %s' % line
        searchObj = re.search(r'SLB中域名(.*)的(.*)状态码速率大于(.*)次/分', line, re.M | re.I | re.S)
        print 'searchObj: %s' % searchObj
        if searchObj:
            print "searchObj.group() : ", searchObj.group()
            print "searchObj.group(1) : ", searchObj.group(1)
            print "searchObj.group(2) : ", searchObj.group(2)
            print "searchObj.group(3) : ", searchObj.group(3)
            d_error[searchObj.group(1)] = searchObj.group(2)
        else:
            print 'Nothing found!'

get_zabbix_alert_list('query',start_time,stop_time)
print d_error

idx_name = 'logstash-slb_%s' % cur_day
stime = int(round(time.time() - 120) * 1000)
dtime = int(round(time.time()) * 1000)
print 'stime: %s,dtime: %s' % (stime,dtime)
def find_es(stime,dtime,idx_name,domain,status):
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
                    {"match_phrase": {"http_host": domain}},
                    {"match": {"status": status}}
                ]
            }
        }
    }
    es = Elasticsearch(hosts='http://10.66.5.28:9200', timeout=300)
    Es_Data = es.search(index='%s' % idx_name, body=body)
    print Es_Data
    print 'Type Es_Data: %s' % type(Es_Data)
    print Es_Data["hits"]["hits"][0]['_source']['remote_addr']
    return Es_Data

def anyls(a):
    import collections
    dic = collections.Counter(a)
    for i in dic:
         # print(i,dic[i])
         d_addr_uri[i] = dic[i]
def cre_str(**kwargs):
    global str_addr_uri
    for key in kwargs:
        print 'first',str_addr_uri
        print "CURRENT :another keyword arg: %s: %s" % (key, kwargs[key]),'!!'
        str_addr_uri = str_addr_uri + ' AND ' + ('%s,%s' % (key, kwargs[key]))
    return str_addr_uri



if d_error:
    for item in d_error:
        print item,'--',d_error[item]
        if int(d_error[item]) == 400 or int(d_error[item]) == 403 or int(d_error[item]) == 404 or int(d_error[item]) == 500:
            # find_es(stime,dtime,idx_name,item,d_error[item])
            for item in find_es(stime,dtime,idx_name,item,d_error[item]):
                l_addr_uri.append('%s-VISIT_URI: %s UPSTREAM_ADDR: %s' % (item['_source']['remote_addr'], item['_source']['request_uri'], item['_source']['upstream_addr']))
                l_readdr.append(item['_source']['remote_addr'])
            anyls(l_addr_uri)
            cre_str(**d_addr_uri)
            for ip in set(l_readdr):
                global str_srv_name
                r = requests.get("http://yunwei.01zhuanche.com/cmdb_query_service?ip=%s" % ip)
                str_srv_name = str_srv_name + 'AND' + ('%s,%s' % (ip, r.text))
            print 'END str_addr_uri: %s' % str_addr_uri
            print 'END srv_name: %s' % str_srv_name
        else:
            print '需人工检查域名对应业务情况'
else:
    print '无域名有400、403、404、500异常'

print '\n'