import networkx as nx
import numpy as np
import json

remain_groundtruth=['votein','LabourIn','LabourIN','jocox','JoCoxMP','GreenerIN','Labour']
leave_groundtruth=['UKIP','BetterOffOut','Nexit','islamic','MakeAmericaGreatAgain','MAGA','Trump','TakeControl']
groundtruth=remain_groundtruth+leave_groundtruth
inital_probabolity_file='inital_probabolity.json'
origin_file_name='dailydata/inconsistency_graph_without_aggregation.graphml'
with open(origin_file_name, mode='r') as f:
    G=nx.read_graphml(origin_file_name)
with open(inital_probabolity_file, mode='r') as f:
    inital_probabolity=json.load(f)

total=0
true=0
total_leave=0
true_leave=0
total_remain=0
true_remain=0
false_leave=0
false_remain=0
for v in G.nodes():
    if G.node[v]['text'] in groundtruth:
        total+=1
        if G.node[v]['sentiment']=='leave' and  G.node[v]['text'] not in leave_groundtruth:
            total_remain+=1
            false_leave+=1
        if G.node[v]['sentiment']=='leave' and  G.node[v]['text'] in leave_groundtruth:
            true+=1
            true_leave+=1
            total_leave+=1
        if G.node[v]['sentiment']=='remain' and  G.node[v]['text'] not in remain_groundtruth:
            total_leave+=1
            false_remain+=1
        if G.node[v]['sentiment']=='remain' and  G.node[v]['text'] in remain_groundtruth:
            true_remain+=1
            total_remain+=1
            true+=1
        if G.node[v]['sentiment']=='remain' and  inital_probabolity[G.node[v]['text']]<0.5:
            print(G.node[v]['timeinterval'],'flip to remain: ', G.node[v]['text'])
        if G.node[v]['sentiment']=='leave' and  inital_probabolity[G.node[v]['text']]>0.5:
            print(G.node[v]['timeinterval'],'flip to leave: ', G.node[v]['text'])
leave_recall=float(true_leave)/total_leave
leave_precision=float(true_leave)/(true_leave+false_leave)
remain_recall=float(true_remain)/total_remain
remain_precision=float(true_remain)/(true_remain+false_remain)
accuracy=float(true)/total
leave_f1=2*float(leave_recall*leave_precision)/(leave_recall+leave_precision)
remain_f1=2*float(remain_recall*remain_precision)/(remain_recall+remain_precision)
print('accuracy: ',accuracy,' leave_recall: ',leave_recall,' leave_precision: ',leave_precision,' remain_recall: ',remain_recall,' remain_precision: ',remain_precision)
print('leave_f1: ',leave_f1,' remain_f1: ',remain_f1)
