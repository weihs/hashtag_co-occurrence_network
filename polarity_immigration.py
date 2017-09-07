import networkx as nx
import yaml

def daily_subgraph(G,timeinterval=1):
    daily_nodes=[v for v in G.nodes() if G.node[v]['timeinterval']==timeinterval]
    subgraph=G.subgraph(daily_nodes)
    return subgraph

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
number_of_days=cfg['number_of_days']
data_directory=cfg['data_directory']
graph_with_label=data_directory+str(number_of_days)+cfg['inference_result_graphml_filename']
origin_aggregated_graph=data_directory+str(number_of_days)+cfg['with_aggregation_graphml_filename']
aggregated_graph_with_label=data_directory+str(number_of_days)+cfg['aggregated_graph_with_label']

with open(graph_with_label, mode='r') as f:
    G1=nx.read_graphml(f)
with open(origin_aggregated_graph, mode='r') as f:
    G2=nx.read_graphml(f)

for day in range(1, number_of_days+1):#label the normal nodes
    SG1=daily_subgraph(G1, day)
    SG2=daily_subgraph(G2, day)
    for v in SG1.nodes():#label the nodes on subgraph
        for u in SG2.nodes():
            if SG1.node[v]['text']==G2.node[u]['text']:
                G2.node[u]['sentiment']=SG1.node[v]['sentiment']
                G2.node[u]['polarity']=SG1.node[v]['polarity']
    # for u in SG2.nodes():#immigrate the labels of subgraph to the graph
    #     G2.node[u]['sentiment']=SG2.node[u]['sentiment']
    #     G2.node[u][]
for v in G2.nodes():#label the pure polarity nodes
    G2.node[v]['text']=G2.node[v]['text']
    if G2.node[v]['text']=='neutral':
        G2.node[v]['sentiment']='neutral'
        G2.node[v]['polarity']=0.0
    elif G2.node[v]['text']=='leave':
        G2.node[v]['sentiment']='leave'
        G2.node[v]['polarity']=-0.5
    elif G2.node[v]['text']=='leave':
        G2.node[v]['sentiment']='remain'
        G2.node[v]['polarity']=0.5

with open(aggregated_graph_with_label, mode='w') as f:
    nx.write_graphml(G2,f)
