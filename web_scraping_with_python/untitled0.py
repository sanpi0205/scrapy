# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 15:04:56 2016

@author: zhangbo
"""

from pyhive import hive
#from TCLIService.ttypes import TOperationState


host = '10.148.10.14'
port = 10000

#host = '10.142.165.7'
#port = 10000

hiveConn = hive.connect(host=host, port=port)
cursor = hiveConn.cursor()

#params = {'dt':'20160731','event_id':'set'}
#query = "select props from dwd.dwd_flow_sdk_phone_event_day where dt='$dt' and event_id='$event_id' limit 10000"

query = "select props['imei'], props['content'] from dwd.dwd_flow_sdk_phone_event_day where dt='20160721' and event_id='set' and app_name='Wallpaper' limit 100000"
cursor.execute(query)
#cursor.execute('show databases')
aa = cursor.fetchall()
print len(aa)

hiveConn.close()


import pymongo
from pymongo import UpdateOne

host = 'localhost'
port = 27017
client = pymongo.MongoClient(host, port)
db = client.test
collection = db.students

a = {
   "_id" : 5,
   "quizzes" : [
      { "wk": 1, "score" : 10 },
      { "wk": 2, "score" : 8 },
      { "wk": 3, "score" : 5 },
      { "wk": 4, "score" : 6 }
   ]
}

collection.insert(a)


#
db.students.update(
   { _id: 5 },
   {
     $push: {
       quizzes: {
          $each: [ { wk: 5, $push:{score: 8} }],
          $sort: { score: -1 },
          $slice: 3
       }
     }
   }
)


query = '''
select a.user_id, a.tag_id, b.pk_wallpaper
from (
select user_id, tag_id, mtime
from dwb.mongo_tags_subscribe 
where status=1 and dt='20160803' 
group by user_id, tag_id, mtime
order by mtime desc 
) a  join 
(select main_tag, pk_wallpaper
from dwb.mysql_wallpaperapi_t_wallpaper
where dt='20160803'
) b on a.tag_id=b.main_tag
where b.main_tag is not null
limit 300
'''


query = '''
select main_tag, pk_wallpaper
from dwb.mysql_wallpaperapi_t_wallpaper
where dt='20160803'
'''



#目标变换数据
rdd1 = sc.parallelize([
    (1, 1),        
    (1, 1),       
    (1, 2),
    (2, 3),    
    (2, 4),
])

rdd1.combineByKey(lambda v:[v],lambda x,y:x+[y],lambda x,y:x+y).collect()

rdd1.collect()
rdd1.reduceByKey(lambda x, y: x )

rdd1.groupByKey()


rdd2 = sc.parallelize([
    (1, 1, 2),
    (1, 1, 5),
    (1, 2, 3),
    (2, 1, 4),
    (2, 2, 5),
])

rdd2.combineByKey(lambda v,w:[v,w],lambda x,y:x+[y],lambda x,y:x+y).collect()


rdd2.reduceByKey(lambda x, y, z: (x,y, [z]) ).collect()
rdd2.groupByKey()

user

import pymongo
client = pymongo.MongoClient('10.73.66.79', 27017)
db = client.wallpaper
collection = db.als

user_list = ['869552022457790', '866646020834779']
user_list = ['']
aa = collection.find({'_id':{"$in": user_list}}, {'recommendation.products':1})
bb = [x for x in aa]






def choose_pages(uid, wallpaper, expected_pages, expected_size):
    recommendation = []
    n = len(wallpaper)
    total = expected_pages * expected_size
    if n >= total:
        for i in range(expected_pages):
            recommendation.append({'uid':uid, 'page':i, 'wallpaper':wallpaper[i:total:expected_size]})
    else:
        pages = n // expected_pages
        rest = n % expected_pages
        if pages == 0:
            recommendation.append({'uid':uid, 'page':0, 'wallpaper':wallpaper})
        else:
            for i in range(pages):
                recommendation.append({'uid':uid, 'page':i, 'wallpaper':wallpaper[i:n:expected_size]})
            if rest > 0:
                recommendation.append({'uid':uid, 'page':i+1, 'wallpaper':wallpaper[i*pages:]})
    return recommendation



result = []
previous_user = ''
previous_tag = ''
wallpaper = []

for uid, tag_id, wallpaper_id in uid_set:
    if uid == previous_user:
        if tag_id == previous_tag:
            n = len(wallpaper)
            #if n >= 3:
            #    previous_tag = tag_id
            #    continue 
            wallpaper.append(wallpaper_id)
        else:            
            wallpaper.append(wallpaper_id)
        previous_tag = tag_id
    else:
        if len(wallpaper) > 0:
            #result.append({'uid':previous_user,'wallpaper':wallpaper})
            result.extend(choose_pages(previous_user, wallpaper, 5, 3))        
        previous_user = uid
        previous_tag = tag_id
        wallpaper = []
        wallpaper.append(wallpaper_id)


#测试
previous_user = ''
previous_tag = ''
wallpaper = []

for uid, tag_id, wallpaper_id in uid_set[:11]:
    
    if uid == previous_user:
        if tag_id == previous_tag:
            n = len(wallpaper)
            #if n >= 3:
            #    previous_tag = tag_id
            #    continue 
            wallpaper.append(wallpaper_id)
        else:            
            wallpaper.append(wallpaper_id)
        previous_tag = tag_id
    else:
        if len(wallpaper) > 0:
            print 'uid is %s, wallpaer is %s' %(previous_user, (',').join(map(str,wallpaper)))
            #result.append({'uid':uid,'wallpaper':wallpaper})
            #result.extend(choose_pages(previous_user, wallpaper, 5, 3))        
        previous_user = uid
        previous_tag = tag_id
        wallpaper = []
        wallpaper.append(wallpaper_id)
    print 'uid is %s, tag_id is %s, wallpaper_id is %s' %(uid, tag_id, wallpaper_id)

len(result)
np.sum([len(x['wallpaper']) for x in result])


aa = choose_pages(uid, wallpaper, 5, 3)
np.sum([len(x['wallpaper']) for x in aa])


a = {'a':1}
def test(a):
    b = a.copy
    b['a'] = 2
    return b

test(a)


u1 = '73469'
u2 = '74903'
matrix[u1][u2]
matrix[u2][u1]