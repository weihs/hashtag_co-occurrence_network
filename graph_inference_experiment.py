import json
import copy
import numpy as np
import networkx as nx
import yaml
from scipy import linalg
from sklearn.preprocessing import normalize

def bound(a):
    threshold=0.000001
    if a<threshold:
        a=threshold
    return a

def daily_subgraph(G,timeinterval=1):
    daily_nodes=[v for v in G.nodes() if G.node[v]['timeinterval']==timeinterval]
    subgraph=G.subgraph(daily_nodes)
    return subgraph

def normalise(a,b):
    offset=0.000001
    if a==0:
        a+=offset
    if b==0:
        b+=offset

    normaliser=a+b
    a=float(a)/normaliser
    b=float(b)/normaliser
    return a,b

def tweetbased_factor_caculation(G,hashtag_classification,inital_probabolity):
    phi={}
    for i in G.nodes():
        if G.node[i]['text'] in hashtag_classification['remain']:#tweet-based factor
            phi[i]=1
        elif G.node[i]['text'] in hashtag_classification['leave']:
            phi[i]=0
        else:
            if G.node[i]['text'] not in inital_probabolity:
                phi[i]=0.5
            else:
                phi[i]=inital_probabolity[G.node[i]['text']]
        if phi[i]==0:
            phi[i]+=0.00001
    return phi

def pagerank(G,hashtag_classification,inital_probabolity,iteration):
    # for v in G.nodes():#delete isolated nodes
    #     if G.degree(v)==0:
    #         G.remove_node(v)
    number_of_nodes=nx.number_of_nodes(G)
    transistion_matrix=np.zeros((number_of_nodes,number_of_nodes))

    i=-1#set the map between id and number
    id_number_hashtable={}
    hashtag_list=[]
    for v in G.nodes():
        i+=1
        id_number_hashtable[v]=i
        hashtag_list.append(G.node[v]['text'])
    hashtag_array=np.array(hashtag_list)
    for v in G.nodes():#consturct and normalize transistion_matrix
        for u in G.neighbors(v):
            transistion_matrix[id_number_hashtable[v]][id_number_hashtable[u]]=G.edge[v][u]['weight']/(G.node[v]['frequency']+G.node[u]['frequency'])
    transistion_matrix=normalize(transistion_matrix,axis=1,norm='l1')

    x=np.ones(number_of_nodes)#tweet-based factor as inital probabolity vector
    for v in G.nodes():
        if G.node[v]['text'] in hashtag_classification['remain']:
            x[id_number_hashtable[v]]=1
        elif G.node[v]['text'] in hashtag_classification['leave']:
            x[id_number_hashtable[v]]=0
        else:
            if G.node[v]['text'] not in inital_probabolity:
                x[id_number_hashtable[v]]=0.5
            else:
                x[id_number_hashtable[v]]=inital_probabolity[G.node[v]['text']]
    x_initial=copy.deepcopy(x)

    for ite in range(iteration):#inference
        x=0.15 + 0.85 * np.dot(transistion_matrix.T,x)
        for i in range(len(x)):
            if x_initial[i]==1:
                x[i]=1
            elif x_initial[i]==0:
                x[i]=0

    b=[{}]
    for v in G.nodes():
        b[0][v]=float(x[id_number_hashtable[v]])
    return b,transistion_matrix,hashtag_array



def lbp_inference(G,hashtag_classification,inital_probabolity,number_of_iteration):
    number_of_nodes=nx.number_of_nodes(G)
    phi=tweetbased_factor_caculation(G, hashtag_classification, inital_probabolity)
    m=[{},{}]
    for i in G.nodes():#initialise message matrix
        m[0][i]={}
        m[1][i]={}
    for i in G.nodes():
        for j in G.neighbors(i):
            m[0][i][j]=1
            m[0][j][i]=1
            m[1][i][j]=1
            m[1][j][i]=1

    for iteration in range(number_of_iteration):#message passing
        for i in G.nodes():
            for j in G.neighbors(i):

                if G.node[i]['text'] in hashtag_classification['remain']:#block the path in seeds
                    m[0][i][j]=1
                    m[1][i][j]=0
                    m[0][i][j], m[1][i][j]=normalise(m[0][i][j], m[1][i][j])
                    continue
                if G.node[i]['text'] in hashtag_classification['leave']:
                    m[0][i][j]=0
                    m[1][i][j]=1
                    m[0][i][j], m[1][i][j]=normalise(m[0][i][j], m[1][i][j])
                    continue

                psi=(G.edge[i][j]['weight'])/(G.node[i]['frequency']+G.node[j]['frequency'])#hashtag-hashtag factor
                m[0][i][j]=0#caculate message
                m[1][i][j]=0
                for k in G.neighbors(i):
                    if k==i:
                        continue
                    m[0][i][j]*=m[0][k][i]
                    m[1][i][j]*=m[1][k][i]
                m[0][i][j]*=psi*phi[i]
                m[1][i][j]*=psi*(1-phi[i])
                # if m[0][i][j]==0 and m[1][i][j]==0:
                #     print(i,j,iteration)
                m[0][i][j], m[1][i][j]=normalise(m[0][i][j], m[1][i][j])

    b=[{}]#assign labels
    for i in G.nodes():
        p_remain=phi[i]
        p_leave=1-phi[i]
        if G.node[i]['text'] in hashtag_classification['remain'] or G.node[i]['text'] in hashtag_classification['leave']:#for seeds do not aggregate messages
            b[0][i]=p_remain
            continue
        for j in G.neighbors(i):#aggregate messages for other nodes
            p_remain+=m[0][j][i]
            p_leave+=m[1][j][i]
        p_remain, p_leave=normalise(p_remain, p_leave)
        b[0][i]=p_remain


    return b,m,phi






def RL_inference(G,hashtag_classification,inital_probabolity):
    number_of_nodes=G.number_of_nodes()
    plotlist=[]
    b=[{},{}]#initialise b
    for v in G.nodes():
        if G.node[v]['text'] in hashtag_classification['remain']:
            b[0][v]=1
        elif G.node[v]['text'] in hashtag_classification['leave']:
            b[0][v]=0
        else:
            if G.node[v]['text'] not in inital_probabolity:
                b[0][v]=0.5
            else:
                b[0][v]=inital_probabolity[G.node[v]['text']]
        b[1][v]=1-b[0][v]

    # remain_counts=0
    # total_counts=0
    # for v in G.nodes():
    #     remain_counts+=G.node[v]['frequency']*inital_probabolity[G.node[v]['text']]
    #     total_counts+=G.node[v]['frequency']
    # p=np.zeros(2)
    # p[0]=float(remain_counts)/total_counts
    # p[1]=1-p[0]
    # r=np.zeros((2,2))
    # for i in range(2):
    #     for j in range(2):


    d={}#set d
    for v in G.nodes():
        d[v]={}
    for u in G.nodes():
        for v in G.nodes():
            if (u,v) in G.edges() or (v,u) in G.edges():
                d[u][v]=G.edge[u][v]['weight']/G.node[u]['frequency']
                #print(u,v,G.edge[u][v]['weight'],d[u][v])
            else:
                d[u][v]=0
    process_visualize(G, b, -1)
    for iteration in range(1):#inference
        for u in G.nodes():
            q0=0
            q1=0
            for v in G.neighbors(u):
                q0+=d[u][v]*b[0][v]
                q1+=d[u][v]*b[1][v]

            alpha=b[0][u]*(1+q0)+b[1][u]*(1+q1)
            b[0][u]=(b[0][u]*(1+q0))/alpha
            b[1][u]=(b[1][u]*(1+q1))/alpha
            if u=='971':
                print(v,q0,b[0][u])
            process_visualize(G, b, iteration)
    return b

def process_visualize(G,b,iteration):
    result_file_name='inference_process_'+str(iteration)+'.gexf'
    for v in G.nodes():
        G.node[v]['sentiment_coefficent']=b[0][v]
        if b[0][v]>0.5:
            G.node[v]['sentiment']='remain'
        elif b[0][v]<0.5:
            G.node[v]['sentiment']='leave'
        else:
            G.node[v]['sentiment']='neutral'

    nx.write_gexf(G,result_file_name)

def set_graph_sentiment(G,sub,b):
    for v in sub.nodes():
        G.node[v]['sentiment_coefficent']=float(b[0][v])
        if b[0][v]>0.5:
            G.node[v]['sentiment']='remain'
        elif b[0][v]<0.5:
            G.node[v]['sentiment']='leave'
        else:
            G.node[v]['sentiment']='neutral'
        G.node[v]['polarity']=b[0][v]-0.5
    return G

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
number_of_days=cfg['number_of_days']
data_directory=cfg['data_directory']
origin_file_name=data_directory+str(number_of_days)+cfg['without_aggregation_graphml_filename']
result_file_name=data_directory+str(number_of_days)+cfg['inference_result_graphml_filename']
classification_file=cfg['classification_file']
inital_probabolity_file=cfg['inital_probabolity_file']
with open(classification_file,mode='r') as f:#load the data
    hashtag_classification=json.load(f)
with open(inital_probabolity_file, mode='r') as f:
    inital_probabolity=json.load(f)
with open(origin_file_name,mode='r') as f:
    G=nx.read_graphml(f)
for day in range(1,number_of_days+1):
    sub=daily_subgraph(G, timeinterval=day)
    b,transistion_matrix,hashtag_array= lbp_inference(sub,hashtag_classification,inital_probabolity,80)
    G=set_graph_sentiment(G, sub, b)
    print('part '+str(day)+'/'+str(number_of_days)+' finished')
# sub=daily_subgraph(G, timeinterval=30)
# #b,transistion_matrix,hashtag_array=pagerank(sub, hashtag_classification, inital_probabolity, 100)
# b,m,phi=lbp_inference(sub,hashtag_classification,inital_probabolity,80)
# G=set_graph_sentiment(sub,b)
with open(result_file_name, mode='w') as f:
    nx.write_graphml(G,f)
