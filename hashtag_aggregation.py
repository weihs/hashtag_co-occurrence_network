import sys
import json
import copy
import yaml
import numpy as np
from scipy import linalg

#the source file offer a set of functions to aggregate hashtag

#aggregate the hashtag frequency list
def aggregate_frequency_list(length=100,
                             origin_file='dailydata/GNIP_hashtag_frequency.json',
                             result_file='dailydata/GNIP_aggregated_hashtag_frequency.json',
                             classification_file='hashtag_classification.json'):
    with open(origin_file,mode='r') as f:#load the data
        hashtag_frequency=json.load(f)
    with open(classification_file,mode='r') as f:#load the data
        hashtag_classification=json.load(f)

    hashtag_label=[3]*length#generate hashtag_label,0:neutral,1:leave,2:remain,3:topic
    for i in range(length):
        if hashtag_frequency[i]['_id'] in hashtag_classification['neutral']:
            hashtag_label[i]=0
        elif hashtag_frequency[i]['_id'] in hashtag_classification['leave']:
            hashtag_label[i]=1
        elif hashtag_frequency[i]['_id'] in hashtag_classification['remain']:
            hashtag_label[i]=2
        else:
            hashtag_label[i]=3

    aggregated_list=[{'_id':'neutral','frequency':0},{'_id':'leave','frequency':0},{'_id':'remain','frequency':0}]#use hashtag_label to aggregate
    for i in range(length):
        if hashtag_label[i]>2:#for a topic hashtag, just copy it
            aggregated_list.append(copy.deepcopy(hashtag_frequency[i]))
        else:#for a polarity hashtag, add it's frequency on the corresponding master hashtag
            aggregated_list[hashtag_label[i]]['frequency']+=hashtag_frequency[i]['frequency']

    with open(result_file,mode='w') as f:#save the aggregated data
        json.dump(aggregated_list,f)

def aggregate_daily_frequency_list(number=50,
                                    length=100,
                                    data_dictionary='dailydata/',
                                    origin_file='dailydata/GNIP_hashtag_daily_frequency_',
                                    result_file='dailydata/GNIP_aggregated_hashtag_daily_frequency_',
                                    classification_filename='hashtag_classification.json'):
    for i in range(1,1+number):
        origin_filename=data_dictionary+origin_file+str(i)+'.json'
        result_filename=data_dictionary+result_file+str(i)+'.json'
        aggregate_frequency_list(length, origin_file=origin_filename, result_file=result_filename, classification_file=classification_filename)
    return

#aggregate a single co_occurrence matrix
def aggregate_daily_cooccurrence_matrix(origin_file='data/npy2/co_occurrence_0.npy',
                                        result_file='data/npy2/aggregated_co_occurrence_0.npy',
                                        classification_file='hashtag_classification.json',
                                        pre_aggregated_list_file='data/json/GNIP_hashtag_frequency.json',
                                        aggregated_list_file='data/json/GNIP_aggregated_hashtag_frequency.json'):
    with open(pre_aggregated_list_file,mode='r') as f:#generate hashtag_label,0:neutral,1:leave,2:remain,3:topic
        hashtag_frequency=json.load(f)
    with open(classification_file,mode='r') as f:
        hashtag_classification=json.load(f)
    with open(origin_file, mode='r') as f:#transform the adjacency matrix
        origin_matrix=np.load(f)
    size=origin_matrix.shape[0]
    length=size
    hashtag_label=[3]*length
    pre_aggregated_list=[d['_id'] for d in hashtag_frequency]
    for i in range(length):
        if hashtag_frequency[i]['_id'] in hashtag_classification['neutral']:
            hashtag_label[i]=0
        elif hashtag_frequency[i]['_id'] in hashtag_classification['leave']:
            hashtag_label[i]=1
        elif hashtag_frequency[i]['_id'] in hashtag_classification['remain']:
            hashtag_label[i]=2
        else:
            hashtag_label[i]=3

    with open(aggregated_list_file,mode='r') as f:#set the value of hashtag_label to indicate the right place in aggregated_list for every hashtag
        aggregated_frequency=json.load(f)
    aggregated_list=[d['_id'] for d in aggregated_frequency]
    for i in range(length):
        if hashtag_label[i]>2:
            hashtag_label[i]=aggregated_list.index(pre_aggregated_list[i])

    result_matrix=np.zeros((size,size), dtype=int)#transform the adjacency matrix
    for i in range(size):
        for j in range(size):
            result_matrix[hashtag_label[i]][hashtag_label[j]]+=origin_matrix[i][j]
    new_size=max(hashtag_label[0:size])+1#reset the size, the size of result_matrix is smaller, so we just need to save part of matrix and the other part is zero
    with open(result_file, mode='w') as f:
        np.save(f,result_matrix[0:new_size,0:new_size])

def aggregate_all_daily_cooccurrence_matrix(number=50,
                                            build_combine_matrix=False,
                                            origin_directory='dailydata/',
                                            result_directory='dailydata/',
                                            classification_file='hashtag_classification.json',
                                            origin_prefix='co_occurrence_',
                                            result_prefix='aggregated_co_occurrence_',
                                            origin_json_prefix='GNIP_hashtag_daily_frequency_',
                                            result_json_prefix='GNIP_aggregated_hashtag_daily_frequency_'):
    postfix='.npy'
    for i in range(1,1+number):
        origin_file=origin_directory+origin_prefix+str(i)+postfix
        result_file=result_directory+result_prefix+str(i)+postfix
        pre_aggregated_list_filename=origin_directory+origin_json_prefix+str(i)+'.json'
        aggregated_list_filename=result_directory+result_json_prefix+str(i)+'.json'
        aggregate_daily_cooccurrence_matrix(origin_file=origin_file, result_file=result_file,classification_file=classification_file,pre_aggregated_list_file=pre_aggregated_list_filename,aggregated_list_file=aggregated_list_filename)
        print(str(i)+'/'+str(number)+' matrices have been aggregated')


#aggregate all cooccurrence_matrices, this is a batch operation
def aggregate_all_cooccurrence_matrices(number=50,
                                        build_combine_matrix=False,
                                        origin_directory='data/npy2/',
                                        result_directory='data/npy2/',
                                        origin_prefix='co_occurrence_',
                                        result_prefix='aggregated_co_occurrence_'):
    postfix='.npy'
    for i in range(number):
        origin_file=origin_directory+origin_prefix+str(i)+postfix
        result_file=result_directory+result_prefix+str(i)+postfix
        aggregate_daily_cooccurrence_matrix(origin_file=origin_file, result_file=result_file)
        print(str(i+1)+'/'+str(number)+' matrices have been aggregated')
    if build_combine_matrix:#if be required to build combine_matrix after transform all daily co_occurrence matrices, build combine co_occurrence matrix
        for i in range(number):
            filename=result_directory+result_prefix+str(i)+postfix
            if i==0:
                combine_matrix=np.load(filename)
            else:
                combine_matrix=linalg.block_diag(combine_matrix,np.load(filename))
        result_file=result_directory+'aggregated_combine_matrix'+postfix
        np.save(result_file,combine_matrix)

def run(number=55,
        build_combine_matrix=False,
        origin_directory='dailydata/',
        result_directory='dailydata/',
        origin_prefix='co_occurrence_',
        result_prefix='aggregated_co_occurrence_',
        origin_json_prefix='GNIP_hashtag_daily_frequency_',
        result_json_prefix='GNIP_aggregated_hashtag_daily_frequency_'):
    aggregate_all_daily_cooccurrence_matrix(number, build_combine_matrix, origin_directory, result_directory, origin_prefix, result_prefix, origin_json_prefix, result_json_prefix)


with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
number_of_days=cfg['number_of_days']
length=cfg['number_of_top_hashtags']
origin_aggregation_list=cfg['origin_aggregation_list']
result_aggregation_list=cfg['result_aggregation_list']
origin_aggregation_matrix=cfg['origin_aggregation_matrix']
result_aggregation_matrix=cfg['result_aggregation_matrix']
classification_file=cfg['classification_file']
data_dictionary=cfg['data_directory']
aggregate_daily_frequency_list(number=number_of_days, length=length, data_dictionary=data_dictionary, origin_file=origin_aggregation_list, result_file=result_aggregation_list, classification_filename=classification_file)
aggregate_all_daily_cooccurrence_matrix(number=number_of_days, build_combine_matrix=False, origin_directory=data_dictionary, result_directory=data_dictionary,classification_file=classification_file, origin_prefix=origin_aggregation_matrix, result_prefix=result_aggregation_matrix, origin_json_prefix=origin_aggregation_list, result_json_prefix=result_aggregation_list)
