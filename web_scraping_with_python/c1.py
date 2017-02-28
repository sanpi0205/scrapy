# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 00:09:06 2016

@author: zhangbo
"""



from urllib import urlopen
from bs4 import BeautifulSoup
html = urlopen("http://www.pythonscraping.com/pages/warandpeace.html")

bsObj = BeautifulSoup(html)
nameList = bsObj.findAll("span", {"class":"green"})

nameList = bsObj.findAll("span", {"class":"green"}) 
for name in nameList:
    print(name.get_text())


5807860 + 2127923+5407059+3757831



from selenium import webdriver
driver = webdriver.PhantomJS(executable_path='/Users/zhangbo/tools/phantomjs/bin/phantomjs')
#driver = webdriver.PhantomJS(executable_path='')
url = "http://epub.sipo.gov.cn/gjcx.jsp"
driver.get(url)


sbox1 = driver.find_element_by_id("opd1")
sbox1.send_keys('20160101')

sbox2 = driver.find_element_by_id("opd2")
sbox2.send_keys('20160701')


div = driver.find_element_by_class_name("gjcx_btn")
link = div.find_elements_by_tag_name("a")
link[1].click()

driver.current_url



submit = driver.find_element_by_class_name("sbtSearch")
submit.click()


aa = driver.find_element_by_id("opd1")
print(driver.find_element_by_id("opd1"))
driver.find_element_by_id("opd1").text = u'sdfsd'

import urllib
import requests
params = {"strWhere":"OPD=BETWEEN['2016.01.01','2016.07.01']"}
url = 'http://epub.sipo.gov.cn/gjcx.jsp'
r = requests.post(url, data=params)
print r.text


js = 'var pato = document.getElementById("pato");setup(pato);pato.pageNow.value = 3;pato.submit();'
driver.execute_script(js)

soup = BeautifulSoup(driver.page_source, 'html.parser')

pages = soup.select('div[class="next"] > a')

nums = []
for page_num in pages:
    try:
        nums.append(int(page_num.text))
    except:
        continue
    
for i in range(page_min, 100, 1):
    old_page_id = driver.find_element_by_tag_name('html').id
    js = 'javascript:zl_fy(%d);' %i
    driver.execute_script(js)
    new_page_id = driver.find_element_by_tag_name('html').id
    while new_page_id == old_page_id:
        time.sleep(0.5)
        new_page_id = driver.find_element_by_tag_name('html').id
    print 'old is %s, new is %s' %(old_page_id, new_page_id)
    
    