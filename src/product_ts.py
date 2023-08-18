
from itertools import product
import networkx as nx
from sympy import symbols

class ProductTs(object):
    def __init__(self) -> None:
        pass
    
    def construct_ts(self, buchi_graph, workspace):
        prod_ts = nx.DiGraph()
        for x, q in list(product(workspace.graph_workspace.nodes(), buchi_graph.nodes())):
            aps = symbols(workspace.get_atomic_prop(x))
            aps_true = {ap: True for ap in aps}
            next_xs = list(workspace.graph_workspace.neighbors(x))  # next_xs includes x
            node_label = buchi_graph.nodes[q]['label']
            if node_label.subs(aps_true):
                for next_x in next_xs:
                    prod_ts.add_edge((x, q), (next_x, q))
            
            next_qs = buchi_graph.succ[q]
            for next_q in next_qs:
                edge_label = buchi_graph.edges[(q, next_q)]['label']
                if edge_label.subs(aps_true):    
                    for next_x in next_xs:
                        prod_ts.add_edge((x, q), (next_x, next_q))
                    
        return prod_ts