from pygraphml import Graph
from pygraphml import GraphMLParser
parser = GraphMLParser()
g = parser.parse('rendered_55days_inconsistency_graph_with_AggregationAndLabel.graphml')
nodes=g.BFS()
for node in nodes:
    node['r']=node['r']
    node['g']=node['g']
    node['b']=node['b']

parser.write(g, "myGraph.graphml")
