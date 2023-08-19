
from itertools import product
import networkx as nx
from sympy import symbols
from buchi import BuchiConstructor

class ProductTs(object):
    def __init__(self) -> None:
        pass
    
    def construct_ts(self, buchi_graph, workspace):
        prod_ts = nx.DiGraph()
        for x, q in list(product(workspace.graph_workspace.nodes(), buchi_graph.nodes())):
            aps_true = symbols(workspace.get_atomic_prop(x))
            next_xs = list(workspace.graph_workspace.neighbors(x))  # next_xs includes x
            node_label = buchi_graph.nodes[q]['label']
            aps_in_label = BuchiConstructor.get_literals(node_label)
            aps_sub = {ap: True if ap in aps_true else False for ap in symbols(aps_in_label)}
            if node_label.subs(aps_sub) == True:
                for next_x in next_xs:
                    weight = 0 if x == next_x else 1
                    prod_ts.add_edge((x, q), (next_x, q), weight=weight)
            
            next_qs = buchi_graph.succ[q]
            for next_q in next_qs:
                edge_label = buchi_graph.edges[(q, next_q)]['label']
                aps_in_label = BuchiConstructor.get_literals(edge_label)
                aps_sub = {ap: True if ap in aps_true else False for ap in symbols(aps_in_label)}
                if edge_label.subs(aps_sub) == True:    
                    for next_x in next_xs:
                        weight = 0 if x == next_x else 1
                        prod_ts.add_edge((x, q), (next_x, next_q), weight=weight)
                    
        return prod_ts