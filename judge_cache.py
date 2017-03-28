#~/usr/bin/python
#-*-coding: utf-8 -*-

import memcache
import requests

mc = memcache.Client(['127.0.0.1:11211'],debug=True)
mc.set('test1','123qwe456asd')
value_test = mc.get('test1')
if value_test == '123qwe456asd':
	print 'Cbase set&get 测试成功...'
	url = raw_input('输入请求URL: ')
	mid = requests.get('%s' % url)
	mc.set('test2','%s' % mid.text)
	value_url = mc.get('test2')
	print '***'
	print 'Response Headers: %s' % mid.headers
	print 'Content-length为: %s' % len(mid.content)
	if len(value_url) == len(mid.content):
		print '接口信息缓存成功...'
	else:
		print '接口信息缓存失败...'
	#print type(mid.text),len(mid.text)
	#print type(mid.content),len(mid.content)
else:
	print 'Cbase set测试失败,需先查看moxi或cbase状态...'
