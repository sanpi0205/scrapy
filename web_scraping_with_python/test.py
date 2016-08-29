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


