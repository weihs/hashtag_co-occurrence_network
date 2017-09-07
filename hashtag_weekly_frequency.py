from pymongo import MongoClient
import numpy as np
from scipy import linalg
import datetime
import json

offset=1
timeinterval_number=17
interval_day=7
end_time=datetime.datetime(2016, 3, 13, 0)


client=MongoClient('146.169.33.33',27020)#build a connection to MongoDB
database=client.get_database('Twitter_DATA')
database.authenticate('twitterApplication','gdotwitter')
collection=database.Twitter_Brexit_GNIP

for i in range(timeinterval_number):
    taglist=[]
    result_file='weeklydata/GNIP_hashtag_weekly_frequency_'+str(offset+i)+'.json'
    start_time=end_time
    end_time=start_time+datetime.timedelta(days=interval_day)
    cursor=collection.aggregate(
        [
            {'$match':{'ISO_created_at':{'$gte':start_time,'$lt':end_time}}},
            {'$unwind':'$hashtags'},
            {'$group':{'_id':'$hashtags','frequency':{'$sum':1}}},
            {'$sort':{'frequency':-1}}
        ]
    )


    for record in cursor:
        taglist.append(record)
    with open(result_file, mode='w') as f:
        json.dump(taglist,f)

    print('finish '+str(offset+i)+'/'+str(timeinterval_number)+' timeintervals')
