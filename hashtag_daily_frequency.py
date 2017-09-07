from pymongo import MongoClient
import numpy as np
from scipy import linalg
import datetime
import json

offset=1
hashtag_number=21
timeinterval_number=10
interval_day=1
duration_in_days=60
end_time=datetime.datetime(2016, 5, 1, 0)
co_occurrence_matrix=np.zeros((hashtag_number,hashtag_number))

client=MongoClient('146.169.33.33',27020)#build a connection to MongoDB
database=client.get_database('Twitter_DATA')
database.authenticate('twitterApplication','gdotwitter')
collection=database.Twitter_Brexit_GNIP

for i in range(duration_in_days):
    taglist=[]
    result_file='dailydata/GNIP_hashtag_daily_frequency_'+str(1+i)+'.json'
    start_time=end_time
    end_time=start_time+datetime.timedelta(days=1)
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
