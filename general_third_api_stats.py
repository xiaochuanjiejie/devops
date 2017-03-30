#!env python
#-*- coding: utf-8 -*-

import os
import sys
import json
import re
import socket
import time
import types
import traceback
import requests

# basic falcon info
step = 60
info_res = {}
metric = 'third-party.log'
agentPostUrl = 'http://localhost:1567/v1/push'
conf = '/usr/local/LeMonitor/falcon-agent/cfg.json'

# file info
LogArr,domain_num  = [],[]
#log_path = '/tmp/info.log'
LogOffSet=50*1024*1024  #Byte
log_time = time.strftime('%Y-%m-%d',time.localtime())
log_path = '/letv/logs/api_request_time.log.%s' % log_time    #生产环境
LogSize=os.stat(log_path).st_size

# 定义json格式
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

# 读取falcon基础信息
def basicinfo(conf):
    with open(conf) as mid:
        source = json.load(mid)
        info_res['hostname'] = source["hostname"]
    return info_res

# 判断域名汇总文件夹是否存在
if os.path.exists('/usr/local/LeMonitor/scripts/checkThird'):
# if os.path.exists('/tmp/scripts/checkThird'):
    pass
else:
    os.makedirs('/usr/local/LeMonitor/scripts/checkThird')
    with open('/usr/local/LeMonitor/scripts/checkThird/domain','w') as f:
        f.write('{''"domains": []''}''\n')
    # os.makedirs('/tmp/scripts/checkThird')
    # with open('/tmp/scripts/checkThird/domain','w') as f:
    #     f.write('{''"domains": []''}''\n')

# 取IP
basicinfo(conf)
ip = str(info_res['hostname'])

# Stastics= {}
# PostArr = []
set_list = []
Trigger = 1000
respstatus = {}
timestatus = {}
Now     = int(time.time())
Date    = time.strftime("%Y-%m-%d %H:%M", time.localtime(Now - 60))
#Date = '2017-03-20 11:07'
Pattern = r'%s:\d+[\|,]\b((?:http|thrift)\b:\/\/[\.\w\-]+).+\|(\d{3})\|(\d+)\|(\d+)$' % Date
# Pattern4xx = r'(4\d+)$'

# 打开增量文件
try:
    FH = open(log_path,'r')
    if LogOffSet >= LogSize:
        LogOffSet = LogSize
    FH.seek(-LogOffSet,2)
    LogArr = FH.readlines()
    FH.close()
except:
    traceback.print_exc()

# 匹配过滤
def ReFilte(x):
    MatchObj = re.match(Pattern,x)
    if MatchObj is not None:
        domain = MatchObj.group(1)
        Domain = {
            domain:{
                'domain': domain,
                'resp_status': MatchObj.group(2),
                'resp_size'  : MatchObj.group(3),
                'resp_time'  : MatchObj.group(4),
            }
        }
        return Domain
mid = map(ReFilte,LogArr)
# 去掉空值等杂质信息
List = [str for str in mid if str not in ['',' ',None]]
#print '正则匹配后的结果: %s' % List

# 匹配第三方汇总文件，进行增量修改
for item in List:
    a = ''.join(item.keys())
    set_list.append(a)
set_list.sort()
set_domains = set(set_list)     #过滤出的域名唯一性
#print '排序后的域名列表: %s' % set_list
#print '过滤出的域名唯一性: %s' % set_domains
# with open('/tmp/scripts/checkThird/domain') as f:
with open('/usr/local/LeMonitor/scripts/checkThird/domain') as f:
    urls = json.load(f)
    for item_url in set_domains:
        if item_url in urls['domains']:
            pass
        else:
            urls['domains'].append(item_url)
    #print type(urls),'读取文件中的domains key: %s' % urls
# f_append = open('/tmp/scripts/checkThird/domain','r+')
f_append = open('/usr/local/LeMonitor/scripts/checkThird/domain','r+')
file = f_append.readlines()
file[0] = '%s\n' % json.dumps(urls)
#f_append = open('/tmp/scripts/checkThird/domain','w+')
f_append = open('/usr/local/LeMonitor/scripts/checkThird/domain','w+')
f_append.writelines(file)
f_append.close()

# for i in set_domains:
#     print 'domain(%s) at %s' % (i,set_list.count(i))

def push_info(set):     #set == set_domains
    # 统计一分钟内第三方域名请求次数
    # with open('/tmp/scripts/checkThird/domain') as f:
    with open('/usr/local/LeMonitor/scripts/checkThird/domain') as f:
        urls = json.load(f)
        for item0 in set:
            if item0 in urls['domains']:
                num = set_list.count(item0)
                domain_num.append({item0:num})
                urls['domains'].remove(item0)
        for zer in urls['domains']:
            num = 0
            domain_num.append({zer:num})
    # 统计一分钟内第三方域名的response status
    # with open('/tmp/scripts/checkThird/domain') as f:
    with open('/usr/local/LeMonitor/scripts/checkThird/domain') as f:
        urls = json.load(f)
        for item1 in List:
            for item2 in urls['domains']:
                item_200 = item2.encode('utf-8') + '-200'
                if respstatus.has_key(item_200) is False:
                    respstatus[item_200] = 0
                item_4xx = item2.encode('utf-8') + '-4xx'
                if respstatus.has_key(item_4xx) is False:
                    respstatus[item_4xx] = 0
                item_5xx = item2.encode('utf-8') + '-5xx'
                if respstatus.has_key(item_5xx) is False:
                    respstatus[item_5xx] = 0
                # print type(item2.encode('utf-8'))     #unicode convert to str
                if item2 in item1.keys() and item1[item2]['resp_status'] == '200':
                    respstatus[item_200] += 1
                elif item2 in item1.keys() and 400 <= int(item1[item2]['resp_status']) < 500:
                    respstatus[item_4xx] += 1
                elif item2 in item1.keys() and 500 <= int(item1[item2]['resp_status']) < 600:
                    respstatus[item_5xx] += 1
    # 统计一分钟内第三方域名超时个数
    # with open('/tmp/scripts/checkThird/domain') as f:
    with open('/usr/local/LeMonitor/scripts/checkThird/domain') as f:
        urls = json.load(f)
        for item3 in List:
            for item4 in urls['domains']:
                item4_mid = item4.encode('utf-8')
                if timestatus.has_key(item4_mid) is False:
                    timestatus[item4_mid] = 0
                if item4 in item3.keys() and int(item3[item4]['resp_time']) > Trigger:
                    timestatus[item4_mid] += 1

    return respstatus,domain_num,timestatus

now = int(time.time())
ts = now - now % int(step)
outlistdata,outreqtimedata,outdictdata = [],[],[]
def postlistdata(data):
    for i in data:
        for (k,v) in i.iteritems():
            tags = 'domain=' + k
            value = v
            counterType = 'GAUGE'
            metric = 'third-domain_nums'
            outlistdata.append(simpleMetric(ip,metric,ts,step,value,counterType,tags))
    return outlistdata
def postreqtimejson(time):
    for (k,v) in time.items():
        tags = 'reqtime>1s:domain=' + k
        value = v
        counterType = 'GAUGE'
        outdictdata.append(simpleMetric(ip,metric,ts,step,value,counterType,tags))
    return outreqtimedata
def postdictjson(*args):
    for turn in args:
        for (k,v) in turn.items():
            tags = 'domain=' + k
            value = v
            counterType = 'GAUGE'
            metric = 'third-resp_status'
            outdictdata.append(simpleMetric(ip,metric,ts,step,value,counterType,tags))
    return outdictdata
def POST(x):
    Respone = requests.post(agentPostUrl,x)
    #print Respone

if __name__ == '__main__':
    push_info(set_domains)
    postlistdata(domain_num)
    postreqtimejson(timestatus)
    postdictjson(respstatus)
    outlistjson = json.dumps(outlistdata,indent=2)
    outreqtimejson = json.dumps(outreqtimedata,indent=2)
    outdictjson = json.dumps(outdictdata,indent=2)
    print outlistjson,outdictjson
    POST(outlistjson)
    POST(outdictjson)
