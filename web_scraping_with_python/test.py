# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 17:33:42 2016

@author: zhangbo
"""

import pymongo

subscribe_mongo = {
	'host': '10.200.91.162',
	'port': 9004,
	'database': 'tags',
	'table': 'subscribe',
	'user': 'zx_am_r',
	'password': 'MWJmMmY4ODc2MWZ'
}

subscribe_mongo_url = "mongodb://zx_am_r:MWJmMmY4ODc2MWZ@10.200.91.145:9004,10.200.91.146:9004,10.200.91.162:9004/tags"
subscribe_client = pymongo.MongoClient(subscribe_mongo_url)

subscribe_db = subscribe_client.tags
subscribe_collection = subscribe_db.subscribe

uids = collection.find({'tag_id':166})
tt = []
for uid in uids:
    tt.append(uid)


from hive import ThriftHive
from hive.ttypes import HiveServerException
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


import pyhs2
 
with pyhs2.connect(host='10.148.10.80',
                   port=10000,
                   authMechanism="PLAIN",
                   user='',
                   password='',
                   database='dwd') as conn:
    with conn.cursor() as cur:
        #Show databases
        print cur.getDatabases()
 
        #Execute query
        cur.execute("select user_id, tag_id from dwb.mongo_tags_subscribe where status=1 and dt='20160725' group by user_id, tag_id, mtime limit 3")
 
        #Return column info from query
        print cur.getSchema()
 
        #Fetch table results
        for i in cur.fetch():
            print i

from pyhive import presto
cursor = presto.connect('10.148.10.80').cursor()
cursor.execute("select user_id, tag_id from dwb.mongo_tags_subscribe where status=1  and dt='20160728' group by user_id, tag_id, mtime limit 3")
print cursor.fetchone()
print cursor.fetchall()


from pyhive import hive
conn = hive.connect('10.148.10.14')
cursor = conn.cursor()
cursor.execute("select * from dwd.dwd_flow_sdk_phone_event_day where dt='20160727' limit 3")
cursor.fetchall()

##bigdata
#from pyhive import hive
#conn = hive.connect('10.142.165.7', 10004)
#cursor = conn.cursor()
#cursor.execute("select * from dwd.dwd_flow_sdk_phone_event_day where dt='20160727' limit 3")
#cursor.fetchall()
#
#
#from pyhive import hive
#conn = hive.connect(host='10.142.165.7', port=10004)
#cursor = conn.cursor()


# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 22:35:38 2016

@author: zhangbo

使用selenium工具以及phantomjs来模拟浏览器
来实现javascript模拟运行，进而实现网络爬虫

"""

import re
from selenium import webdriver
driver = webdriver.PhantomJS(executable_path='/Users/zhangbo/tools/phantomjs/bin/phantomjs')

url = "http://epub.sipo.gov.cn/gjcx.jsp"
driver.get(url)


sbox1 = driver.find_element_by_id("opd1")
sbox1.send_keys('20160101')

sbox2 = driver.find_element_by_id("opd2")
sbox2.send_keys('20160201')


div = driver.find_element_by_class_name("gjcx_btn")
link = div.find_elements_by_tag_name("a")
link[1].click()

driver.current_url

div = driver.find_element_by_class_name("next")
link = div.find_elements_by_tag_name("a")





f1 = driver.find_element_by_class_name("cp_linr")

#driver.find_element_by_link_text
data = dict()

header =  f1.find_element_by_tag_name("h1").text

category = re.findall(r'\[(.*?)\]', header)[0]
title = re.sub(r'(\[.*\])|\s', '', header)

if data.get('category', None) is None:
    data['category'] = category

if data.get('title', None) is None:
    data['title'] = title

table = f1.find_elements_by_tag_name("li")

for a in table:
    if a.text != '':
        try:
            unfold_link = a.find_element_by_tag_name('a')
            #作者
            if unfold_link.get_attribute("class") == 'zhankaizt':
                '''作者展开
                '''
                unfold_link.click()  #展开作者信息
                authors = re.sub(u'\u2002', '', a.text) #去除空格
                authors = re.split(u'：', authors)
                if len(authors) == 2:
                    if data.get(authors[0], None) is None:
                        data[authors[0]] = authors[1]
                else:
                    print u'作者信息错误'
                unfold_link.click() #收起
                
            if unfold_link.get_attribute("class") == 'zhankai':
                '''分类号展开
                '''
                category_id = re.sub(u'全部', '', a.text)
                category_id = re.split(u'：', category_id)
                if len(category_id) == 2:
                    if data.get(category_id[0], None) is None:
                        data[category_id[0]] = category_id[1]
                else:
                    print u'代理机构信息有误'
                unfold_link.click() #展开
                sub_links = a.find_elements_by_tag_name("li")
                for link in sub_links:
                    sub_text = link.text
                    sub_text = re.split(u'：', sub_text)
                    if len(sub_text) == 2:
                        if data.get(sub_text[0], None) is None:
                            data[sub_text[0]] = sub_text[1]
                unfold_link.click() #收起            
        except:
            #print u'其他无需收起开关的信息'
            information = re.split(u'：', a.text)
            if len(information) == 2:
                if data.get(information[0], None) is None:
                    data[information[0]] = information[1]
            else:
                print u'%s 出现错误' %information

#
substract = f1.find_element_by_class_name('cp_jsh')
try :
    unfold = substract.find_element_by_class_name('zhankaizy')
    unfold.click() #展开摘要
    n = len(substract.text)
    substract_text = substract.text[:(n-2)]   #去掉‘收起’这个词
    unfold.click() #收起
except:
    substract_text = substract.text

#摘要中文本较长，其中存在使用冒号情况，因而不能使用文本切分。
if substract_text[:2] == u'摘要':
    if data.get(u'摘要', None) is None:
        data[u'摘要'] = substract_text[3:]
else:
    print u'摘要解析错误'

        
        
    


for key, value in data.items():
    print key + ":" + value

                    


re.search('[*]', title)




def get_data_period(dt1, dt2):
    return


