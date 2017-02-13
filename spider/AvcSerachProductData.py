# -*- coding:utf-8 -*-

import requests
import redis
import json
import time
import threading
from HTMLParser import HTMLParser
from datetime import datetime
import re
import sys
default_encoding = "utf-8"
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


# 存放采集手机数据的redis key name
redis_key_phone_w = "dpc_phone_url:start_urlsssss"
# 读取筛选无效的手机数据，过滤
redis_key_invalid_r = "dpc_phone_url:item_invalid"
# 读取手机redis key name--"dpc_phone_keywords:item_keywords"
redis_key_phone_model = "dpc_phone_url:item_keywords"
# 代理ip
redis_key_proxy = "proxy:iplist4"

# 连接redis
rconnection_yz = redis.Redis(host='117.122.192.50', port=6479, db=0)
# 存放数据，测试使用,正常发布任务，该处需要注释
# rconnection_test = redis.Redis(host='1.119.7.234', port=26479, db=0)
rconnection_test = redis.Redis(host='192.168.2.245', port=6379, db=0)
# 2017-02-10 11:49:35.608000
# 设置循环次数，如果超过该次数，则跳出
errorCount = 2

# 存放搜索无效的关键词
invalid_keywords = rconnection_test.lrange(redis_key_invalid_r, 0, -1)

JD_url = "http://item.jd.com/{0}.html"
TM_url = "http://detail.tmall.com/item.htm?id={0}&amp;areaid=&amp;"
SN_url = "http://product.suning.com/{0}.html"
YMX_url = "https://www.amazon.cn/dp/{0}"
YHD_url = "https://www.amazon.cn/dp/{0}"
# 京东搜索按【评论数】排序
search_JD_url = "https://search.jd.com/Search?keyword={0}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&psort=4&click=0"
# 天猫搜索按照【综合】排序
search_TM_url = "https://list.tmall.com/search_product.htm?q={0}&type=p"
# 苏宁搜索按照【评论数】排序
search_SN_url = "http://search.suning.com/emall/searchProductList.do?keyword={0}&pg=01&st=6"
# 亚马逊 搜索按照【相关度】排序
search_YMX_url = "https://www.amazon.cn/s/field-keywords={0}"
# 一号店 搜索按照【评论数】排序
search_YHD_url = "http://search.yhd.com/c-/k{0}/#page=1&sort=5"


def search_TM(keybrand, keywords,topcount):
    # 天猫搜索按照综合排序
    url = search_TM_url.format(keywords)
    # print url
    sesson = requests.session()
    isValue = True
    index = 0
    isvaluecount = 0
    while isValue:
        if errorCount < index:
            print "%s: TM not find this keywords : %s" % (datetime.now(), keywords)
            break
        # 随机获取代理ip
        proxy = rconnection_yz.srandmember(redis_key_proxy)
        proxyjson = json.loads(proxy)
        proxiip = proxyjson["ip"]
        sesson.proxies = {'http': 'http://' + proxiip, 'https': 'https://' + proxiip}
        try:
            print "------proxy_ip---%s" % proxyjson["ip"]
            req = sesson.get(url, timeout=30)
            html = req.text
            req.close()
            isValue = False
            if html:
                # print html
                tzurl = re.findall(r'(<a href="//detail.tmall.com/item.htm?)+(.*)(</a>)', html)
                if tzurl:
                    for i in tzurl:
                        # print i[1]
                        if len(i) == 3:
                            # print i[1]
                            # 开始查找id号,
                            search_id = re.search("(id=(?P<dd>.*?))+(&amp;skuId)", i[1])
                            if search_id:
                                # 截取页面信息id
                                spid = search_id.group("dd")
                                # print spid
                                # 截取页面信息商品名称
                                search_spname = re.search("(title=.*)+(>.*)", i[1])
                                if search_spname:
                                    spname = search_spname.group()
                                    # print spname
                                    # 判断是否无效,如果isspnameTrue 为True,则表示无效数据，过滤，如果为False，表示是有效数据
                                    isspnameTrue = False
                                    for ia in invalid_keywords:
                                        if ia in spname and "送" not in spname:
                                            isspnameTrue = True
                                    if isspnameTrue == True:
                                        # print "------invalid data TM，pass------"
                                        continue
                                    else:
                                        result_url=TM_url.format(spid)
                                        result = '{"attrs":{"category":"手机","brand":"%s","model":"%s","urlweb":"TM"},"url":"%s"}'% (keybrand,keywords,result_url)
                                        # 拼写json类型保存至redis
                                        # print result
                                        if isvaluecount == topcount:
                                            break
                                        else:
                                            isvaluecount += 1
                                            rconnection_test.lpush(redis_key_phone_w, result)
                                else:
                                    print "%s:can not find TM url spname,please search regular is valid" % datetime.now()
                            else:
                                print "%s:can not find TM url id,please search regular is valid" % datetime.now()
                else:
                    print "%s:TM url---the first regular is valid ?" % datetime.now()
        except Exception, e:
            isValue = True
            index += 1
            print "connection redis error: %s , %s" % (index, e)
            time.sleep(5)


def search_JD(keybrand, keywords,topcount):
    # 京东搜索按照综合排序
    url = search_JD_url.format(keywords)
    sesson = requests.session()
    isValue = True
    index = 0
    isvaluecount = 0
    while isValue:
        if errorCount < index:
            print "%s: JD not find this keywords : %s" % (datetime.now(), keywords)
            break
        # 随机获取代理ip
        proxy = rconnection_yz.srandmember(redis_key_proxy)
        proxyjson = json.loads(proxy)
        proxiip = proxyjson["ip"]
        sesson.proxies = {'http': 'http://' + proxiip, 'https': 'https://' + proxiip}
        try:
            print "------proxy_ip---%s" % proxyjson["ip"]
            req = sesson.get(url, timeout=30)
            req.encoding = "UTF-8"
            html = req.text
            isValue = False
            if html:
                # print html
                tzurl = re.findall(r'(<a target="_blank" title=")(.*)[\s\S](.*)(</em>)', html)
                if tzurl:
                    for i in tzurl:
                        if len(i) == 4:
                            # 开始查找id号,
                            search_id = re.search('(href="//item.jd.com/(?P<dd>\d+))', i[1])
                            if search_id:
                                # 截取页面信息id
                                spid = search_id.group("dd")
                                # print spid
                                # 截取页面信息商品名称
                                search_spname = i[2]
                                if search_spname:
                                    spname = search_spname
                                    # print spname
                                    # 判断是否无效,如果isspnameTrue 为True,则表示无效数据，过滤，如果为False，表示是有效数据
                                    isspnameTrue = False
                                    for ia in invalid_keywords:
                                        if ia in spname and "送" not in spname:
                                            isspnameTrue = True
                                    if isspnameTrue == True:
                                        # print "------invalid data JD，pass------"
                                        continue
                                    else:
                                        result_url = JD_url.format(spid)
                                        result = '{"attrs":{"category":"手机","brand":"%s","model":"%s","urlweb":"JD"},"url":"%s"}'% (keybrand,keywords,result_url)
                                        # 拼写json类型保存至redis
                                        # print result
                                        if isvaluecount == topcount:
                                            break
                                        else:
                                            isvaluecount += 1
                                            rconnection_test.lpush(redis_key_phone_w, result)
                                else:
                                    print "%s:can not find JD url spname,please search regular is valid" % datetime.now()
                            else:
                                print "%s:can not find JD url id,please search regular is valid" % datetime.now()
                else:
                    print "%s:JD url---the first regular is valid ?" % datetime.now()
        except Exception, e:
            isValue = True
            index += 1
            print "connection redis error: %s , %s" % (index, e)
            time.sleep(5)


def search_SN(keybrand, keywords,topcount):
    # 苏宁搜索按照综合排序
    url = search_SN_url.format(keywords)
    sesson = requests.session()
    isValue = True
    index = 0
    isvaluecount = 0
    while isValue:
        if errorCount < index:
            print "%s: SN not find this keywords : %s" % (datetime.now(), keywords)
            break
        # 随机获取代理ip
        proxy = rconnection_yz.srandmember(redis_key_proxy)
        proxyjson = json.loads(proxy)
        proxiip = proxyjson["ip"]
        sesson.proxies = {'http': 'http://' + proxiip, 'https': 'https://' + proxiip}
        try:
            print "------proxy_ip---%s" % proxyjson["ip"]
            req = sesson.get(url, timeout=30)
            req.encoding = "UTF-8"
            html = req.text
            isValue = False
            if html:
                # print html
                tzurl = re.findall(r'(target="_blank" href="http://product.suning.com/)(.*)', html)
                if tzurl:
                    # print tzurl
                    for i in tzurl:
                        if len(i) == 2:
                            # 开始查找id号,
                            # search_id = re.search('(href="//item.jd.com/(?P<dd>\d+))', i[1])
                            search_id = re.search('(?P<dd>\d+/\d+)(.html">)', i[1])
                            if search_id:
                                # 截取页面信息id
                                spid = search_id.group("dd")
                                # print spid
                                # 截取页面信息商品名称
                                search_spname = i[1]
                                if search_spname:
                                    spname = search_spname
                                    # print spname
                                    # 判断是否无效,如果isspnameTrue 为True,则表示无效数据，过滤，如果为False，表示是有效数据
                                    isspnameTrue = False
                                    for ia in invalid_keywords:
                                        if ia in spname and "送" not in spname:
                                            isspnameTrue = True
                                    if isspnameTrue == True:
                                        # print "------invalid data SN，pass------"
                                        continue
                                    else:
                                        result_url = SN_url.format(spid)
                                        result = '{"attrs":{"category":"手机","brand":"%s","model":"%s","urlweb":"SN"},"url":"%s"}'% (keybrand,keywords,result_url)
                                        # 拼写json类型保存至redis
                                        # print result
                                        if isvaluecount == topcount:
                                            break
                                        else:
                                            isvaluecount += 1
                                            rconnection_test.lpush(redis_key_phone_w, result)
                                else:
                                    print "%s:can not find SN url spname,please search regular is valid" % datetime.now()
                            else:
                                print "%s:can not find SN url id,please search regular is valid" % datetime.now()
                else:
                    print "%s:SN url---the first regular is valid ?" % datetime.now()
        except Exception, e:
            isValue = True
            index += 1
            print "connection redis error: %s , %s" % (index, e)
            time.sleep(5)


def search_YMX(keybrand, keywords,topcount):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0)"
    }
    url = search_YMX_url.format(keywords)

    sesson = requests.session()
    isValue = True
    index = 0
    isvaluecount = 0
    while isValue:
        if errorCount < index:
            print "%s: YMX not find this keywords : %s" % (datetime.now(), keywords)
            break
        # 随机获取代理ip
        proxy = rconnection_yz.srandmember(redis_key_proxy)
        proxyjson = json.loads(proxy)
        proxiip = proxyjson["ip"]
        sesson.proxies = {'http': 'http://' + proxiip, 'https': 'https://' + proxiip}
        try:
            print "------proxy_ip---%s" % proxyjson["ip"]
            req = sesson.get(url, headers=header, timeout=30)
            req.encoding = "utf-8"
            html = req.text
            isValue = False
            if html:
                html = HTMLParser().unescape(html)
                # print html
                tzurl = re.findall(r'(<a class="a-link-normal s-access-detail-page  a-text-normal" target="_blank" title=")(.*)(</h2>)', html)
                if tzurl:
                    # print tzurl
                    for i in tzurl:
                        # print i[1]
                        if len(i) == 3:
                            # 开始查找id号,
                            # search_id = re.search('(href="//item.jd.com/(?P<dd>\d+))', i[1])
                            search_id = re.search('(href="https://www.amazon.cn/dp/)(?P<dd>.*)("><h2)', i[1])
                            if search_id:
                                # 截取页面信息id
                                spid = search_id.group("dd")
                                # print spid
                                # 截取页面信息商品名称
                                search_spname = i[1]
                                if search_spname:
                                    spname = search_spname
                                    # print spname
                                    # 判断是否无效,如果isspnameTrue 为True,则表示无效数据，过滤，如果为False，表示是有效数据
                                    isspnameTrue = False
                                    for ia in invalid_keywords:
                                        if ia in spname and "送" not in spname:
                                            isspnameTrue = True
                                    if isspnameTrue == True:
                                        # print "------invalid data YMX，pass------"
                                        continue
                                    else:
                                        result_url = YMX_url.format(spid)
                                        result = '{"attrs":{"category":"手机","brand":"%s","model":"%s","urlweb":"YMX"},"url":"%s"}'% (keybrand,keywords,result_url)
                                        # 拼写json类型保存至redis
                                        # print result
                                        if isvaluecount == topcount:
                                            break
                                        else:
                                            isvaluecount += 1
                                            rconnection_test.lpush(redis_key_phone_w, result)
                                else:
                                    print "%s:can not find YMX url spname,please search regular is valid" % datetime.now()
                            else:
                                print "%s:can not find YMX url id,please search regular is valid" % datetime.now()
                else:
                    print "%s:YMX url---the first regular is valid ?" % datetime.now()
        except Exception, e:
            isValue = True
            index += 1
            print "connection redis error: %s , %s" % (index, e)
            time.sleep(5)


def search_YHD(keybrand, keywords,topcount):
    # 一号店搜索按照综合排序
    url = search_YHD_url.format(keywords)
    sesson = requests.session()
    isValue = True
    index = 0
    isvaluecount = 0
    while isValue:
        if errorCount < index:
            print "%s: YHD not find this keywords : %s" % (datetime.now(), keywords)
            break
        # 随机获取代理ip
        proxy = rconnection_yz.srandmember(redis_key_proxy)
        proxyjson = json.loads(proxy)
        proxiip = proxyjson["ip"]
        sesson.proxies = {'http': 'http://' + proxiip, 'https': 'https://' + proxiip}
        try:
            print "------proxy_ip---%s" % proxyjson["ip"]
            req = sesson.get(url, timeout=30)
            req.encoding = "UTF-8"
            html = req.text
            isValue = False
            if html:
                # print html
                tzurl = re.findall(r'(class="mainTitle")+(.*)', html)
                if tzurl:
                    # print tzurl
                    for i in tzurl:
                        if len(i) == 2:
                            # 开始查找id号,
                            # search_id = re.search('(href="//item.jd.com/(?P<dd>\d+))', i[1])
                            search_id = re.search(r'(href="http://item.yhd.com/item/)(?P<dd>\d+)', i[1])
                            if search_id:
                                # 截取页面信息id
                                spid = search_id.group("dd")
                                # print spid
                                # 截取页面信息商品名称
                                search_spname = re.search(r'(title=".*?")', i[1])
                                if search_spname:
                                    spname = search_spname.group()
                                    # 判断是否无效,如果isspnameTrue 为True,则表示无效数据，过滤，如果为False，表示是有效数据
                                    isspnameTrue = False
                                    for ia in invalid_keywords:
                                        if ia in spname and "送" not in spname:
                                            isspnameTrue = True
                                    if isspnameTrue == True:
                                        # print "------invalid data YHD，pass------"
                                        continue
                                    else:
                                        result_url = YHD_url.format(spid)
                                        result = '{"attrs":{"category":"手机","brand":"%s","model":"%s","urlweb":"YHD"},"url":"%s"}'% (keybrand,keywords,result_url)
                                        # 拼写json类型保存至redis
                                        # print result
                                        if isvaluecount == topcount:
                                            break
                                        else:
                                            isvaluecount += 1
                                            rconnection_test.lpush(redis_key_phone_w, result)
                                else:
                                    print "%s:can not find YHD url spname,please search regular is valid" % datetime.now()
                            else:
                                print "%s:can not find YHD url id,please search regular is valid" % datetime.now()
                else:
                    print "%s:YHD url---the first regular is valid ?" % datetime.now()
        except Exception, e:
            isValue = True
            index += 1
            print "connection redis error: %s , %s" % (index, e)
            time.sleep(5)


if True:
    # 读取手机型号
    keyisvalue = rconnection_test.keys(redis_key_phone_model)
    if keyisvalue:
        print keyisvalue
        # 读取品牌型号搜索

    else:
        print "没有找到key"

    print "start : %s" % datetime.now()
    while True:
        axw = rconnection_test.lpop(redis_key_phone_model)
        if axw:
            modeljson = json.loads(axw)
            model = modeljson["model"]
            brand = modeljson["brand"]
            # 开始下载数据 设置多线程 15
            threads = []
            threads.append(threading.Thread(target=search_TM, args=(brand, model, 3)))
            threads.append(threading.Thread(target=search_JD, args=(brand, model, 3)))
            threads.append(threading.Thread(target=search_SN, args=(brand, model, 3)))
            threads.append(threading.Thread(target=search_YHD, args=(brand, model, 3)))
            threads.append(threading.Thread(target=search_YMX, args=(brand, model, 3)))
            for tx in threads:
                tx.start()
            for tx in threads:
                tx.join()
        else:
            break
    print "end : %s" % datetime.now()
