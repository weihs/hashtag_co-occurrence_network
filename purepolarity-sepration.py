import json
import copy
import yaml
import numpy as np
import networkx as nx
from scipy import linalg

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
number_of_days=cfg['number_of_days']
data_directory=cfg['data_directory']
origin_file_name=data_directory+str(number_of_days)+cfg['aggregated_graph_with_label']
pure_polarity_file_name=data_directory+str(number_of_days)+cfg['pure-polarity_graphml_filename']
main_graph_file_name=data_directory+str(number_of_days)+cfg['main-part_graphml_filename']

with open(origin_file_name,mode='r') as f:
    G=nx.read_graphml(f)

polaritylist=['remain','leave','neutral']
polarityset=set([v for v in G.nodes() if G.node[v]['text'] in polaritylist])
H=G.subgraph(polarityset)
G.remove_nodes_from(polarityset)

with open(pure_polarity_file_name, mode='w') as f:
    nx.write_graphml(H,f)
with open(main_graph_file_name, mode='w') as f:
    nx.write_graphml(G,f)
