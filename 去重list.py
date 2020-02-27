#!/usr/bin/python
# coding: utf-8

list_number=[1,2,3,4,5,6,6,7,7,7,8,9]


def anyls(a):
    import collections
    dic = collections.Counter(a)
    for i in dic:
         print i,dic[i]

anyls(list_number)