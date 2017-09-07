import networkx as nx
import json
import re

def get_tags_from_tweet(tweet):
    word_list=re.findall(r"#(\w+)", tweet)
    tag_list=[]
    for word in word_list:
        if len(word)<1:
            continue
        tag_list.append(word)
    return tag_list

def count_tweet(remain_table,total_table,tag_list,remain_signal):
    if remain_signal=='unkown':
        return
    for tag in tag_list:
        if tag in remain_table and remain_signal=='remain':
            remain_table[tag]+=1
        elif remain_signal=='remain':
            remain_table[tag]=1
        if tag in total_table:
            total_table[tag]+=1
        else:
            total_table[tag]=1
    return

def caculate_probability(remain_table,total_table,inital_probabolity):
    for key in remain_table.keys():
        probability=float(remain_table[key])/total_table[key]
        inital_probabolity[key]=probability
    return

origin_file_name='svm_classified.graphml'
result_file_name='inital_probabolity.json'
remain_table={}
total_table={}
inital_probabolity={}

with open(origin_file_name,mode='r') as f:
    G=nx.read_graphml(f)

for v in G.nodes():
    if 'tweet' not in G.node[v]:
        continue
    tag_list=get_tags_from_tweet(G.node[v]['tweet'])
    count_tweet(remain_table,total_table,tag_list,G.node[v]['brexit'])
caculate_probability(remain_table, total_table, inital_probabolity)

with open(result_file_name, mode='w') as f:
    json.dump(inital_probabolity,f,sort_keys=True)
