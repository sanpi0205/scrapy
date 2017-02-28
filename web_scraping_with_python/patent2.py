# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 22:35:38 2016

@author: zhangbo

使用selenium工具以及phantomjs来模拟浏览器
来实现javascript模拟运行，进而实现网络爬虫

本次修改：
1.去掉页面内的click操作；
2.以专利号作为"_id"索引

"""

import numpy as np
import sys
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pymongo
import datetime
import time
from bs4 import BeautifulSoup


def parse_one_category(driver):
    
    print u''
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pages = soup.select('div[class="next"] > a')
    nums = []
    for page_num in pages:
        try:
            nums.append(int(page_num.text))
        except:
            continue
    page_min = np.min(nums) #取出一个
    page_max = np.max(nums)

    alldata = []
    total_patents = 0
    total_time = 0
    for i in range(page_min, page_max + 1, 1):
        startTime = datetime.datetime.now()

        #js = '''
        #var pato = document.getElementById("pato");
        #setup(pato);pato.pageNow.value = %d;
        #pato.submit();
        #'''
        old_page_id = driver.find_element_by_tag_name('html').id
        js = 'javascript:zl_fy(%d);' %i
        driver.execute_script(js)
        new_page_id = driver.find_element_by_tag_name('html').id

        start_loop_timing = datetime.datetime.now()
        while new_page_id == old_page_id:
            time.sleep(2)
            new_page_id = driver.find_element_by_tag_name('html').id
            end_loop_timing = datetime.datetime.now()
            loop_time_consume = (end_loop_timing - start_loop_timing).seconds
            if loop_time_consume > 10:
                print u'警告， 可能陷入死循环, 已耗时 %s 秒, old_id 是 %s， new_id 是 %s' %(loop_time_consume, old_page_id, new_page_id)
            if loop_time_consume > 30:
                print u'强制退出'
                break


        soup = BeautifulSoup(driver.page_source, 'html.parser')
        patents_one_page = bs_parse_onepage(soup)
        n = len(patents_one_page)
        total_patents += n
        alldata.extend(patents_one_page)

        endTime = datetime.datetime.now()
        time_consumed_per_page = (endTime - startTime).seconds
        total_time += time_consumed_per_page

        print u'完成第 %d 页, 耗时 %d 秒, 共耗时 %d 秒, 抓取记录 %d 条，共 %d 条' %(i, time_consumed_per_page, total_time, n, total_patents)

        n_alldata = len(alldata)
        if n_alldata > 200:
            upload_to_mongo(alldata)
            alldata = [] #清空 alldata 数据
            print u'上传 %d 条记录，已经上传 %d 条记录' %(n_alldata, total_patents)

    # startTime = datetime.datetime.now()
    # alldata = bs_parse_onepage(driver)
    # endTime = datetime.datetime.now()
    # print u'完成第 1 页, 共耗时 %d 秒'  %(endTime - startTime).seconds

    # num_pages = 1
    # is_completed = True
    # total_patents = len(alldata)

    # while is_completed:
    #     startTime = datetime.datetime.now()
    #     div = driver.find_element_by_class_name("next")
    #     try:
    #         next_page = div.find_element_by_link_text(">")
    #         #跳转至下一页
    #         next_page.click()
    #         num_pages += 1
    #         data_in_onepage = bs_parse_onepage(driver)
    #         alldata.extend(data_in_onepage)
    #         total_patents += len(data_in_onepage)
    #     except:
    #         is_completed = False
        
    #     endTime = datetime.datetime.now()
    #     print u'完成第 %d 页, 共耗时 %d 秒, 抓取记录 %d 条，共 %d 条' %(num_pages, (endTime - startTime).seconds, len(data_in_onepage), total_patents)

    #     n_alldata = len(alldata)
    #     if n_alldata == 200:
    #         upload_to_mongo(alldata)
    #         #total_patents += len(alldata)
    #         alldata = []
    #         print u'上传 %d 条记录，已经上传 %d 条记录' %(n_alldata, total_patents)

    if n_alldata > 0 :
        upload_to_mongo(alldata)
        print  u'上传 %d 条记录，已经上传 %d 条记录' %(n_alldata, total_patents)

    print u'共收集 %d 页数据, %d 条记录' %(page_max, total_patents)
    
    return True


def bs_parse_onepage(soup):
    '''
    '''
    #soup = BeautifulSoup(driver.page_source, 'html.parser')
    patents = soup.find_all('div', class_='cp_box')
    data_onepage = []
    for patent in patents:
        data_onepage.append(bs_parse_patent(patent))
    return data_onepage

def bs_parse_patent(patent):
    '''用 beautiful soup 解析单条数据
    '''
    data = dict()
    patent_content = patent.find('div', class_='cp_linr')

    header = patent_content.h1.text
    header = re.sub(u'\u2002', '', header)
    category = re.findall(r'\[(.*?)\]', header)[0]
    title = re.sub(r'(\[.*\])|\s', '', header)

    if data.get('category', None) is None:
        data['category'] = category
    
    if data.get('title', None) is None:
        data['title'] = title

    table = patent_content.find_all('li')

    for li in table:
        if li.text != '':
            #判断作者信息是否需要展开，如果需要则解析
            if li.find('a', class_='zhankaizt') is not None:
                #authors = re.sub(r'', repl, string)
                li.a.replaceWith('')
                authors = re.sub(u'\u2002', '', li.text)
                authors = re.split(u'：', authors)
                if len(authors) == 2:
                    if data.get(authors[0], None) is None:
                        data[authors[0]] = authors[1]
                    else:
                        print u'作者信息错误'

            #判断分类号是否需要展开
            if li.find('a', class_='zhankai') is not None:
                li.a.replaceWith('')
                sub_ul = li.find('ul')
                category_id = ''
                if sub_ul is not None:
                    #抽取ul下所有li，进行遍历
                    li_list = sub_ul.find_all('li')
                    for sub_li in li_list:
                        sub_li_text = sub_li.text
                        if re.search(u'：', sub_li_text) is None:
                            #如果是None,即是分类号后半部分
                            category_id = sub_li_text
                        else:
                            #如果不是None, 则说明是另一个字段
                            sub_text = re.split(u'：', sub_li_text)
                            if len(sub_text) == 2:
                                if data.get(sub_text[0], None) is None:
                                    data[sub_text[0]] = sub_text[1]
                            else:
                                #分类号中有多个冒号，区分
                                print u'分类号中 %s 有误' %sub_li_text
                                continue #如果有误直接跳过这一条
                li.ul.replaceWith('')
                category_id = li.get_text(strip=True) + category_id
                category_id = re.split(u'：', category_id)
                if len(category_id) == 2:
                    if data.get(category_id[0], None) is None:
                        data[category_id[0]] = category_id[1]
                else:
                    print u'分类信息有误'

            #其他无展开 u'其他无需收起开关的信息'
            if li.find('a', class_='zhankai') is None and li.find('a', class_='zhankaizt') is None:
                information = re.split(u'：', li.text)
                if len(information) == 2:
                    #判断 申请公布号 与 授权公布号
                    if data.get(information[0], None) is None:
                        data[information[0]] = information[1]
                #else:
                #    print u'%s 出现错误' %information

    substract = patent.find('div',class_='cp_jsh')
    if substract.find('a') is not None:
        substract.a.replaceWith('')
    substract_text = substract.get_text(strip=True)
    
    #摘要中文本较长，其中存在使用冒号情况，因而不能使用文本切分。
    if substract_text[:2] == u'摘要':
        if data.get(u'摘要', None) is None:
            data[u'摘要'] = substract_text[3:]
    else:
        print u'摘要解析错误'

    return data

        
def upload_to_mongo(data):
    
    host = '10.73.66.79'
    port = 27017
    client = pymongo.MongoClient(host, port) #10.154.156.118
    db = client.patent
    collection = db.patent

    bulk = collection.initialize_unordered_bulk_op()
    for item in data:
        bulk.find({'_id': item[u'申请公布号']}).upsert().update({'$set': {'patent': item}})
    bulk.execute()
    #collection.insert_many(data)
    #print u'上传 %d 条数据' %len(data)
    

if __name__ == '__main__':

    if len(sys.argv) > 3:
        print sys.argv
        sys.exit(u'抓取程序需要输入两个时间段')
    date1 = str(sys.argv[1])
    if len(date1) != 8:
        sys.exit('please use the rigth format for the date yyyymmdd')
    date2 = str(sys.argv[2])
    if len(date2) != 8:
        sys.exit('please use the rigth format for the date yyyymmdd')

    phantomjs_path = '/Users/zhangbo/tools/phantomjs/bin/phantomjs'  # mac path
    #phantomjs_path = '/home/zhangbo/software/phantomjs/bin/phantomjs'
    driver = webdriver.PhantomJS(executable_path=phantomjs_path)
    url = "http://epub.sipo.gov.cn/gjcx.jsp"
    driver.get(url)
    print driver.current_url

    #高级查询中选择时间段
    sbox1 = driver.find_element_by_id("opd1")
    sbox1.send_keys('20160101')
    #sbox1.send_keys(str(date1))
    sbox2 = driver.find_element_by_id("opd2")
    sbox2.send_keys('20160201')
    #sbox2.send_keys(str(date2))
    
    #跳转至patentoutline页面
    div = driver.find_element_by_class_name("gjcx_btn")
    link = div.find_elements_by_tag_name("a")
    link[1].click()
    print driver.current_url
    
    #每页显示条数
    select_size_onepage = Select(driver.find_element_by_id("ts"))
    select_size_onepage.select_by_value("10")
    
    #选择页面中 “发明公布”， 默认选择
    #driver.execute_script("javascript:zl_lx('pip')")
    print u'开始爬取 发明公布 数据'
    alldd = parse_one_category(driver)
    
    #选择页面中 “发明授权”， 默认选择
    print u'开始爬取 发明授权 数据'
    driver.execute_script("javascript:zl_lx('pig')")
    alldd = parse_one_category(driver)

    #选择页面中 “实用新型”， 默认选择
    print u'开始爬取 实用新型 数据'
    driver.execute_script("javascript:zl_lx('pug')")
    alldd = parse_one_category(driver)

    #选择页面中 “外观设计”， 默认选择
    print u'开始爬取 外观设计 数据'
    driver.execute_script("javascript:zl_lx('pdg')")
    alldd = parse_one_category(driver)


    
    driver.close()
    
