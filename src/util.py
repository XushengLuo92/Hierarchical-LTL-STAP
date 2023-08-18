import networkx as nx 
import subprocess
import argparse

def vis_graph(graph, title, latex=False, buchi_graph=False):
    # write dot file to use with graphviz
    graph_copy = graph.copy()
    if buchi_graph:
        for node in graph_copy.nodes():
            graph_copy.nodes[node]['label'] =  graph_copy.nodes[node]['name'] + '  ' + str(graph_copy.nodes[node]['label'])
    # run "dot -Tpng test.dot >test.png"
    nx.nx_agraph.write_dot(graph_copy, title+'.dot')
    # add the following the generated dot file
    # rankdir=LR;
	# node [texmode="math"];
    # dot2tex --preproc --texmode math ./data/task_network.dot | dot2tex > ./data/task_network.tex
    if not latex:
        # Run a Linux command
        command = "dot -Tpng {0}.dot >{0}.png".format(title)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
    else:
        command = "dot2tex {0}.dot --preproc > {0}.tex".format(title)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
def create_parser():
    """ create parser

    Returns:
        _type_: _description_
    """
    parser = argparse.ArgumentParser(description='FM')
    parser.add_argument('--task', default="man", type=str)
    parser.add_argument('--case', default=0, type=int)
    parser.add_argument('--vis', action='store_true', help='Enable visualization')
    parser.add_argument('--dot', action='store_true', help='Enable dot graph')

    return parser


def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
 
 
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
 
 
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
 
 
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
 
 
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
 
 
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
 
 
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
 
 
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))
 