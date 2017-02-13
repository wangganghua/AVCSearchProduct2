# encoding:utf8


import redis
import json
from lxml import etree
from selenium import webdriver
from HTMLParser import HTMLParser
# 2017-02-09 17:48:23.869000
redis_key_proxy = "proxy:iplist4"
rconnection_test = redis.Redis(host='192.168.2.245', port=6379, db=0, charset="utf-8")
rconnection_yz = redis.Redis(host='117.122.192.50', port=6479, db=0)
# rconnection_test = redis.Redis(host='1.119.7.234', port=26479, db=0, charset="utf-8")


def texd():
    # url = "https://detail.tmall.com/item.htm?id=530268236010&ns=1&abbucket=4"
    url = "http://product.dangdang.com/1296143735.html"

    # driver = webdriver.PhantomJS()
    proxy = rconnection_yz.srandmember(redis_key_proxy)
    proxyjson = json.loads(proxy)
    proxiip = proxyjson["ip"]
    print proxiip
    # proxydriver = webdriver.Proxy()
    # # proxydriver.proxy_type=ProxyType
    # proxydriver.http_proxy=proxiip
    # proxydriver.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
    # driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)

    # driver = webdriver.PhantomJS(service_args=[
    #                         '--proxy=' + proxiip,
    #                         '--proxy-type=http'
    #                     ])
    driver = webdriver.PhantomJS()
    try:
     driver.get(url)
     xpth = '//div[@id="pc-price"]'
     html = driver.find_element_by_xpath(xpth)
     print html.text
    except Exception,e:
        print e
    driver.quit()
    # html = '<?xml version="1.0" encoding="ISO-8859-1"?> <bookstore><book><title lang="eng">Harry Potter</title><price>29.99</price></book><book>  <title lang="eng">Learning XML</title>  <price>39.95</price></book></bookstore>'
    # tree = etree.HTML(html)

def retext1():
    wx = open("F:\wgh.txt")
    for i in wx:
        print i.decode("gbk")
        rconnection_test.lpush("price_test_time:start_urls", i.decode("gbk"))
    print "end"

    # 手机
def retext():
    wx = open("F:\/brandmodel.txt")
    for i in wx:
        print i.decode("gbk")
        rconnection_test.lpush("dpc_phone_url:item_keywords", i.decode("gbk"))
    print "end"
def retext2():
    wx = open("F:\collect_url.txt")
    for i in wx:
        print i

texd()