#-*- coding: utf-8 -*-
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

# 判断存放域名汇总文件夹是否存在
if os.path.exists('/usr/local/sso_third_domain'):
    pass
else:
    os.makedirs('/usr/local/sso_third_domain')
    with open('/usr/local/sso_third_domain/domain','w') as f:
        f.write('{''"domains": []''}''\n')

# if os.path.exists('/tmp/sso_third_domain'):
#     pass
# else:
#     os.makedirs('/tmp/sso_third_domain')
#     with open('/tmp/sso_third_domain/domain','w') as f:
#         # f.write('{''\n''\t "domains": []''\n''}''\n')
#         f.write('{''"domains": []''}''\n')

# basic falcon info
tmp1,result_domain,result_ip,domain_num = [],[],[],[]
# conf = '/users/xujunchuan/documents/cfg.json'
conf = '/usr/local/lemonitor/falcon-agent/cfg.json'
agentposturl = 'http://localhost:1567/v1/push'
metric = 'sso.log'
endpoint = '10.148.16.174'
step = 60

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

# basic filter info
ISOTIMEFORMAT='%Y/%m/%d'
ISOTIMEFORMAT_2='%d %H:%M:'
before_time = time.time() - 60
# 测试环境文件路径
# file_path = '/tmp/info.log'
# 生产环境文件路径
file_path = '/data/behavior/sso/curlMonitor/%s' % time.strftime(ISOTIMEFORMAT,time.localtime())
file_time = time.strftime(ISOTIMEFORMAT_2,time.localtime(before_time))
#print 'file_path: %s\nfile_time: %s' % (file_path,file_time)

# filter file
# 测试环境过滤
# last_minute_file = Popen('grep "27 00:00:" /tmp/info.log',shell=True, stdout=PIPE, stderr=PIPE)
# 生产环境过滤
last_minute_file = Popen('grep "%s" %s/info.log' % (file_time,file_path),shell=True, stdout=PIPE, stderr=PIPE)
stdout = last_minute_file.communicate()
file_mid = "".join(stdout)
filter_result = file_mid.split('\n')
#print type(filter_result),'filter_result: %s' % filter_result

for line in filter_result:
    if not line.strip():continue
    # print line.split('#')[2].split(':')[1]
    if float(line.split('#')[2].split(':')[1]) > 1000.0 or line.find("timed out"):
        ip  = line.split()[3]
        domain = line.split('#')[4].split('/')[2]
        tmp1.append({ip:domain})
        result_domain.append(domain)
        result_ip.append(ip)

# 去重domain，并记录至/usr/local/sso_third_domain文件夹下
result_domain.sort()
set_domain = set(result_domain)
# with open('/tmp/sso_third_domain/domain') as f:
with open('/usr/local/sso_third_domain/domain') as f:
    urls = json.load(f)
    for iteritems in set_domain:
        if iteritems in urls['domains']:
            pass
        else:
            urls['domains'].append(iteritems)
    #print type(urls),'读取文件中的domains key: %s' % urls
#追加第三方域名
# f_append = open('/tmp/sso_third_domain/domain','r+')
f_append = open('/usr/local/sso_third_domain/domain','r+')
file = f_append.readlines()
file[0] = '%s\n' % json.dumps(urls)
# f_append = open('/tmp/sso_third_domain/domain','w+')
f_append = open('/usr/local/sso_third_domain/domain','w+')
f_append.writelines(file)
f_append.close()


# with open('/tmp/sso_third_domain/domain') as f:
with open('/usr/local/sso_third_domain/domain') as f:
    urls = json.load(f)
    for item in set_domain:
        if item in urls['domains']:
            num = result_domain.count(item)
            domain_num.append({item:num})
            urls['domains'].remove(item)
    for zer in urls['domains']:
        num = 0
        domain_num.append({zer:num})
now = int(time.time())
ts = now - now % int(step)
outdata = []
for i in domain_num:
    for (k,v) in i.iteritems():
        tags = 'domain=' + k
        value = v
        counterType = 'GAUGE'
        outdata.append(simpleMetric(endpoint,metric,ts,step,value,counterType,tags))
#print outdata
outjson = json.dumps(outdata,indent=2)
#print outjson
m=requests.post(agentposturl,outjson)
