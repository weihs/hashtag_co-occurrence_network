import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import yaml
from colour import Color

#generate a gradient colo map
def color_list_generator(color_level=100,start_color='white',end_color='red'):
    start=Color(color=start_color)
    end=Color(color=end_color)
    color_list=list(start.range_to(end,color_level))
    return color_list

#visualization the color map
def color_list_visualization(color_list):
    for i in range(len(color_list)):
        plt.plot([i,i],c=color_list[i].get_rgb())
    plt.show()

#assign every edge a color with regard to its realweight
def color_weight_hash(G,weight_attribute='weight'):
    weight=[int(G[u][v][weight_attribute]) for u,v in G.edges()]
    color_level=-1
    color_weight_hash=np.zeros(max(weight)+1).astype(int)
    for i in range(max(weight)+1):
        if i in weight:
            color_level+=1
            color_weight_hash[i]=color_level
    return color_weight_hash,color_level+1

#coloring verical edges according to color_weight_hashtable
def vertical_edge_coloring(G,color_weight_hash,color_list,type_attribute='type'):
    i=0
    for u,v in G.edges():
        if G.edge[u][v][type_attribute]==0:
            color=color_list[color_weight_hash[int(G.edge[u][v]['weight'])]].get_rgb()
            G.edge[u][v]['r']=int(color[0]*255)
            G.edge[u][v]['g']=int(color[1]*255)
            G.edge[u][v]['b']=int(color[2]*255)
            i+=1
            #plt.plot([i,i],c=color)


#coloring horizetal edges accorind to thhe source node
def horizental_edge_coloring(G,type_attribute='abs'):
    for u,v in G.edges():
        if G.edge[u][v][type_attribute]==1:
            if G.node[u]['sentiment']==G.node[v]['sentiment']:
                G.edge[u][v]['r']=0
                G.edge[u][v]['g']=0
                G.edge[u][v]['b']=255
            else:
                G.edge[u][v]['r']=0
                G.edge[u][v]['g']=255
                G.edge[u][v]['b']=0

# remove those nodes which have no link with other nodes in the same period
def node_filter_by_degree(G,weight=200,type_attribute='abs'):
    timeinterval_list=[G.node[v]['timeinterval'] for v in G.nodes()]
    max_timeinterval=max(timeinterval_list)
    for v in G.nodes():
        if v not in G.edge or len(G.edge[v])==0:
            G.remove_node(v)
            continue
        if len(G.edge[v])==2 and G.node[v]['timeinterval']>0 and G.node[v]['timeinterval']<max_timeinterval:
            new_edge=G.edge[v].keys()# build a new edge btween its two adjacent nodes
            G.add_edge(new_edge[0],new_edge[1])
            G.edge[new_edge[0]][new_edge[1]][type_attribute]=1
            G.edge[new_edge[0]][new_edge[1]]['weight']=weight
            G.edge[new_edge[0]][new_edge[1]]['r']=G.node[v]['r']
            G.edge[new_edge[0]][new_edge[1]]['g']=G.node[v]['g']
            G.edge[new_edge[0]][new_edge[1]]['b']=G.node[v]['b']
            G.remove_node(v)#remove this node
            continue
        if len(G.edge[v])==1:
            G.remove_node(v)

def edge_filter(G):
    pure_polarity=['leave','remain','neutral']
    for u,v in G.edges():
        if (G.node[u]['text'] in pure_polarity or G.node[v]['text'] in pure_polarity) and G.edge[u][v]['type']==0:
            G.remove_edge(u,v)

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
number_of_days=cfg['number_of_days']
data_directory=cfg['data_directory']
origin_file_name=data_directory+str(number_of_days)+cfg['aggregated_graph_with_label']
result_file_name=data_directory+str(number_of_days)+cfg['rendered_graphml_filename']
with open(origin_file_name,mode='r') as f:
    G=nx.read_graphml(f,int)
edge_filter(G)
color_weight_hash,color_level=color_weight_hash(G, weight_attribute='weight')
color_list=color_list_generator(color_level=color_level, start_color='white', end_color='red')
vertical_edge_coloring(G, color_weight_hash, color_list, type_attribute='type')
horizental_edge_coloring(G, type_attribute='type')


#node_filter_by_degree(G, weight=200, type_attribute='abs')

for v in G.nodes():
    #G.node[v]['log_gravity_y']=float(np.log2(G.node[v]['frequency']+1))
    G.node[v]['minus_log_gravity_y']=float(-1*np.log2(G.node[v]['frequency']+1))
    #G.node[v]['polarity_scale']=G.node[v]['polarity']*100
    #G.node[v]['minus_polarity_scale']=-1*G.node[v]['polarity']*100
    #G.node[v]['label']=G.node[v]['text']
    #G.node[v]['y']=-1*float(G.node[v]['y'])

nx.write_graphml(G,result_file_name)
