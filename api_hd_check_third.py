# -*- coding: utf-8 -*-
__author__ = 'xujunchuan'

from subprocess import PIPE,Popen
import re
import time
import os
import json
import time
import socket
import requests
import sys
import getopt

endpoint = '10.110.80.71'
step = 60
metric = 'api-hd.log'
agentPostUrl   = 'http://localhost:1567/v1/push'

def simpleMetric(endpoint,metric,ts,step,value,counterType,tags):
    data = {
        "endpoint": endpoint,
        "metric": metric,
        "timestamp": ts,
        "step": step,
        "value": value,
        "counterType": counterType,
        "tags": tags
    }
    return data

ISOTIMEFORMAT='%Y/%m/%d'
ISOTIMEFORMAT_2='%H:%M:'
before_time = time.time() - 60
file_path = '/data/behavior/hd/http/%s' % time.strftime(ISOTIMEFORMAT, time.localtime())
file_time = time.strftime(ISOTIMEFORMAT_2,time.localtime(before_time))
print file_time,'---',file_path
chat = ["10.110.50.25","10.110.50.26","10.110.60.44","10.110.60.45","10.130.208.70","10.130.91.108","10.180.219.132","10.180.91.145","10.183.91.26","10.183.91.27"]
vcm = ["10.110.50.21","10.110.50.22","10.110.60.42","10.110.60.43","10.130.208.72","10.130.91.111","10.180.219.55","10.180.244.191","10.183.91.28","10.183.91.29"]
vcs = ["10.110.50.77","10.110.60.46","10.110.60.59","10.130.211.100","10.130.91.185","10.180.244.134","10.180.244.195","10.183.91.33","10.183.101.98","10.183.101.99","10.183.101.40","10.183.101.41","10.183.101.42","10.183.99.76","10.183.99.80","10.183.99.82","10.183.99.83","10.183.99.53"]
other = ["10.110.60.47","10.110.60.48","10.110.60.49","10.130.91.120","10.180.219.70","10.180.244.133","10.183.91.31","10.183.91.32"]
action = ["10.110.60.50","10.110.60.57","10.110.60.58","10.130.91.174","10.180.226.210","10.183.91.30"]
danmu = ["10.110.50.76","10.110.60.60","10.130.91.204","10.130.208.74","10.180.91.146","10.183.91.34"]
url_list = ['10.100.2.246:28018','api.live.letv.com','api.my.letv.com','api.sso.letv.com','i.api.letv.com','i.msg.letv.com','msg.touch.letv.com','static.api.letv.com','top.letv.com','yuanxian.letv.com']

last_minute_file = Popen('grep "%s" %s/info.log' % (file_time,file_path),shell=True, stdout=PIPE, stderr=PIPE)
# last_minute_file = Popen('grep "19:08:" /tmp/info.log',shell=True, stdout=PIPE, stderr=PIPE)
stdout = last_minute_file.communicate()
file_1 = "".join(stdout)
file_2 = file_1.split('\n')
# print file_2,'22222222222222222'
list_url_chat,list_url_vcm,list_url_vcs,list_url_other,list_url_action,list_url_danmu = [],[],[],[],[],[]
for line in file_2:
    if not line.strip():continue
    if float(line.split()[8].split(':')[1]) > 1000.0:
        ip = line.split()[3]
        url = line.split()[6].split('/')[2]
        if ip in chat:
            list_url_chat.append(url)
        elif ip in vcm:
            list_url_vcm.append(url)
        elif ip in vcs:
            list_url_vcs.append(url)
        elif ip in other:
            list_url_other.append(url)
        elif ip in action:
            list_url_action.append(url)
        elif ip in danmu:
            list_url_danmu.append(url)

def filtration(result):
    t_dict = globals()
    result.sort()
    name = ''
    for key in t_dict:
        if type(t_dict[key]) is type(result) and t_dict[key] == result and len(result) > 1:
            name = key
    set_result = set(result)
    if name:
        tmp1 = []
        outdata = []
        for item in set_result:
            a = item
            b = result.count(item)
            tmp1.append({a:b})
        print tmp1,type(tmp1)
        now = int(time.time())
        ts = now - now % int(step)

       # with open('/tmp/%s.json' % name,'w') as f_tmp1:
       #     f_tmp1.write(json.dumps(tmp1))

        for i in tmp1:
            for (k,v) in i.iteritems():
                # print "dict[%s] =" % k, v
                if k in url_list:
                    tags = 'domain=' + k
                    value  = v
                    counterType = 'GAUGE'
                    outdata.append(simpleMetric(endpoint,metric,ts,step,value,counterType,tags))
                    url_list.remove(k)
        #无超时第三方置空
        for zer in url_list:
            tags = 'domain=' + zer
            value = 0
            counterType = 'GAUGE'
            outdata.append(simpleMetric(endpoint,metric,ts,step,value,counterType,tags))
        outjson = json.dumps(outdata,indent=1)
        #print outjson,type(outjson),'*******************************'
        m=requests.post(agentPostUrl,outjson)
    else:
        #无第三方超时的模块置空
        outdata = []
        now = int(time.time())
        ts = now - now % int(step)
        for zer1 in url_list:
            tags = 'domain=' + zer1
            value = 0
            counterType = 'GAUGE'
            outdata.append(simpleMetric(endpoint,metric,ts,step,value,counterType,tags))
        outjson = json.dumps(outdata,indent=1)
        #print outjson,type(outjson),'*******************************'
        m=requests.post(agentPostUrl,outjson)

	#outdata.append(simpleMetric(endpoint,metric,ts,step,value,counterType,tags))
	# outjson = json.dumps(tmp1,indent=1)
	# print outjson,type(outjson)

filtration(list_url_chat)
filtration(list_url_vcm)
filtration(list_url_vcs)
filtration(list_url_action)
filtration(list_url_danmu)
filtration(list_url_other)
