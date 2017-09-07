from pymongo import MongoClient
import numpy as np
import json
from scipy import linalg
import datetime
from pprint import *


offset=51
hashtag_number=100
timeinterval_number=10
interval_day=1
end_time=datetime.datetime(2016, 6,20)
co_occurrence_matrix=np.zeros((hashtag_number,hashtag_number))

client=MongoClient('146.169.33.33',27020)#build a connection to MongoDB
database=client.get_database('Twitter_DATA')
database.authenticate('twitterApplication','gdotwitter')
collection=database.Twitter_Brexit_GNIP

for timeinterval in range(timeinterval_number):#get co_occurrence matrix for every timeinterval
    start_time=end_time# construct the date constraint
    end=start_time+datetime.timedelta(days=interval_day)
    hashtaglist_filename='dailydata/GNIP_hashtag_daily_frequency_'+str(offset+timeinterval)+'.json'#construct the hashtag list
    with open(hashtaglist_filename, mode='r') as f:
        hashtaglist=json.load(f)
    hashtag=[item['_id'] for item in hashtaglist]

    for i in range(hashtag_number-1):#count the co_occurrence frequency of every pair of hashtags by MongoDB
        for j in range(i,hashtag_number):
            co_occurrence_matrix[i][j]=collection.find({'ISO_created_at':{'$gte':start_time,'$lt':end},'hashtags':{'$all':[hashtag[i],hashtag[j]]}},{'ISO_created_at':1,'hashtags':1}).count()
    with open('dailydata/co_occurrence_'+str(offset+timeinterval)+'.npy', mode='w') as f:
        np.save(f,co_occurrence_matrix)


#for i in range(timeinterval_number):#build combine co_occurrence matrix
#    filename='dailydata/co_occurrence_'+str(offset+i)+'.npy'
#    if i==0:
#        combine_matrix=np.load(filename)
#    else:
#        combine_matrix=linalg.block_diag(combine_matrix,np.load(filename))
#np.save('dailydata/combine_matrix',combine_matrix)
