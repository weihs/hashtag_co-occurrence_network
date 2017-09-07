import json
import copy
import yaml
import sys
import numpy as np
import networkx as nx
from scipy import linalg


def merge_cooccurrence_matrix(number_of_days, origin_directory,result_directory,origin_prefix,result_filename):
    postfix='.npy'
    for i in range(1,1+number_of_days):#build combine co_occurrence matrix
        filename=origin_directory+origin_prefix+str(i)+postfix
        if i==1:
            combine_matrix=np.load(filename)
        else:
            new_matrix=np.load(filename)
            combine_matrix=linalg.block_diag(combine_matrix,new_matrix)

    result_file=result_directory+result_filename
    np.save(result_file,combine_matrix)
    return combine_matrix


def construct_graphml(number_of_days,combine_matrix,origin_directory,origin_prefix,hashtag_frequency_prefix):
    G=nx.from_numpy_matrix(combine_matrix)
    prenode=0
    for i in range(1,1+number_of_days):#add node attributes
        daily_matrix_filename=origin_directory+origin_prefix+str(i)+'.npy'#get the number of hashtag
        matrix=np.load(daily_matrix_filename)
        number_of_hashtag=matrix.shape[0]

        filename=origin_directory+hashtag_frequency_prefix+str(i)+'.json'#construct graph and set node attributes
        with open(filename, mode='r') as f:
            hashtag_frequency=json.load(f)
        for j in range(number_of_hashtag):
            G.node[prenode+j]['text']=hashtag_frequency[j]['_id']
            G.node[prenode+j]['frequency']=hashtag_frequency[j]['frequency']
            G.node[prenode+j]['timeinterval']=i
        prenode+=j+1


    for v in G.nodes():#connect the same node in two closet period
        text=G.node[v]['text']
        same_text_nodelist=[u for u in G.nodes() if G.node[u]['text']==text and u>v]
        if len(same_text_nodelist)==0:
            continue
        else:
            u=min(same_text_nodelist)
            G.add_edge(u,v)
            G.edge[u][v]['type']=1
            G.edge[u][v]['weight']=10
    for u,v in G.edges():# set type attributes for vertical edges and remove self-loop
        if 'type' not in G.edge[u][v]:
            G.edge[u][v]['type']=0
        if u==v:
            G.remove_edge(u,v)
    return G

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

number_of_days=cfg['number_of_days']
data_directory=cfg['data_directory']

if sys.argv[1]=='without_aggregation':
    origin_prefix=cfg['origin_aggregation_matrix']
    hashtag_frequency_prefix=cfg['origin_aggregation_list']
    graphml_filename=data_directory+str(number_of_days)+cfg['without_aggregation_graphml_filename']
    result_filename=cfg['without_aggregation_combine_matrix']
else:
    origin_prefix=cfg['result_aggregation_matrix']
    hashtag_frequency_prefix=cfg['result_aggregation_list']
    graphml_filename=data_directory+str(number_of_days)+cfg['with_aggregation_graphml_filename']
    result_filename=cfg['with_aggregation_combine_matrix']




combine_matrix=merge_cooccurrence_matrix(number_of_days, data_directory, data_directory, origin_prefix, result_filename)
G=construct_graphml(number_of_days, combine_matrix, data_directory,origin_prefix,hashtag_frequency_prefix)

with open(graphml_filename,mode='w') as f:
    nx.write_graphml(G,f)
