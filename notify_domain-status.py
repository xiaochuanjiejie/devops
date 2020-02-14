#!/usr/bin/python
# coding: utf-8

import re
import time
import requests
import datetime

'''
SLB中域名mc-im.01zhuanche.com的500状态码速率大于5次/分
'''

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
    for line in info:
        searchObj = re.search(r'SLB中域名(.*)的(.*)状态码速率大于(.*)次/分', line, re.M | re.I | re.S)
        if searchObj:
            print "searchObj.group() : ", searchObj.group()
            print "searchObj.group(1) : ", searchObj.group(1)
            print "searchObj.group(2) : ", searchObj.group(2)
            print "searchObj.group(3) : ", searchObj.group(3)
        else:
            print 'Nothing found!'

get_zabbix_alert_list('query','20200213143000','20200213150000')