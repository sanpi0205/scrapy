# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 22:35:38 2016

@author: zhangbo

使用selenium工具以及phantomjs来模拟浏览器
来实现javascript模拟运行，进而实现网络爬虫

"""

import sys
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pymongo
import datetime


def parse_one_category(driver):
    
    startTime = datetime.datetime.now()
    alldata = parse_onepage(driver)
    endTime = datetime.datetime.now()
    print u'完成第 1 页, 共耗时 %d 秒'  %(endTime - startTime).seconds
    is_completed = True
    num_pages = 1
    while is_completed:
        div = driver.find_element_by_class_name("next")
        try:
            next_page = div.find_element_by_link_text(">")
            #跳转至下一页
            next_page.click()
            num_pages += 1
            startTime = datetime.datetime.now()
            data_in_onepage = parse_onepage(driver)
            endTime = datetime.datetime.now()
            print u'完成第 %d 页, 共耗时 %d 秒' %(num_pages, (endTime - startTime).seconds)
            alldata.extend(data_in_onepage)
        except:
            is_completed = False
    print u'共收集 %d 页数据' %num_pages
    print u'包括 %d 条数据' %len(alldata)
    return alldata


def parse_onepage(driver):
    patents = driver.find_elements_by_class_name("cp_linr")
    data_onepage = []
    for patent in patents:
        data_onepage.append(parse_patent(patent))
    return data_onepage


def parse_patent(patent):
    data = dict()    
    header =  patent.find_element_by_tag_name("h1").text
    
    category = re.findall(r'\[(.*?)\]', header)[0]
    title = re.sub(r'(\[.*\])|\s', '', header)
    
    if data.get('category', None) is None:
        data['category'] = category
    
    if data.get('title', None) is None:
        data['title'] = title
    
    table = patent.find_elements_by_tag_name("li")
    
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
    substract = patent.find_element_by_class_name('cp_jsh')
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
    
    return data

        
def upload_to_mongo(data):
    
    client = pymongo.MongoClient('localhost', 27017) #10.154.156.118
    db = client.patent
    #写入壁纸使用频率
    collection = db.patent
    collection.insert_many(data)
    print u'上传 %d 条数据' %len(data)
    

if __name__ == '__main__':

    if len(sys.argv) > 3:
        print sys.argv
        sys.exit(u'抓取程序需要输入两个时间段')
    data1 = str(sys.argv[1])
    if len(data1) != 8:
        sys.exit('please use the rigth format for the date yyyymmdd')
    data2 = str(sys.argv[1])
    if len(data1) != 8:
        sys.exit('please use the rigth format for the date yyyymmdd')

    driver = webdriver.PhantomJS(executable_path='/Users/zhangbo/tools/phantomjs/bin/phantomjs')
    url = "http://epub.sipo.gov.cn/gjcx.jsp"
    driver.get(url)
    
    sbox1 = driver.find_element_by_id("opd1")
    sbox1.send_keys('20160101')
    
    sbox2 = driver.find_element_by_id("opd2")
    sbox2.send_keys('20160201')
    
    #跳转至patentoutline页面
    div = driver.find_element_by_class_name("gjcx_btn")
    link = div.find_elements_by_tag_name("a")
    link[1].click()
    print driver.current_url
    
    #每页显示条数
    select_size_onepage = Select(driver.find_element_by_id("ts"))
    select_size_onepage.select_by_value("10")
    
    #driver.execute_script("javascript:zl_lx('pigc')")
    alldd = parse_one_category(driver)
    
    #upload_to_mongo(alldd)
    
    driver.close()
    
