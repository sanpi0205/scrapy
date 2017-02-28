import sys
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pymongo
import datetime

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


select_size_onepage = Select(driver.find_element_by_id("ts"))
select_size_onepage.select_by_value("10")

print driver.current_url

source = driver.page_source

from bs4 import BeautifulSoup

soup = BeautifulSoup(source, 'html.parser')

patents = soup.find_all('div', class_='cp_box')
patent = soup.find('div', class_='cp_linr')

header = patent.h1.text
category = re.findall(r'\[(.*?)\]', header)[0]
title = re.sub(r'(\[.*\])|\s', '', header)

table = patent.find_all('li')


#driver.execute_script("javascript:zl_lx('pigc')")

driver.execute_script("var pato = document.getElementById('pato')")
var pato = document.getElementById("pato")
setup(pato)
pato.pageNow.value = '2'
pato.submit()


html_doc = '''
<li>分类号：B29C70/34(2006.01)I;&nbsp;&nbsp;<a href="javascript:;" class="zhankai" style="color:#c5000f">全部</a><div style="display:none;"><ul>
						<li>&ensp;B29C70/44(2006.01)I;&ensp;B29C70/54(2006.01)I</li>
						<li>专利代理机构：中国航空专利中心11008</li><li>代理人：陈宏林</li></ul></div></li>

'''
aa = BeautifulSoup(html_doc, 'html.parser')

print aa.get_text(strip=True)

re.sub(u'\u2002','',aa.get_text(strip=True))


aa = bs_parse_onepage(driver)