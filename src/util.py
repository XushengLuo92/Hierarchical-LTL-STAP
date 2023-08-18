import networkx as nx 
import subprocess
import argparse
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np 

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

def plot_workspace(workspace, ax):
    plt.rc('text', usetex=False)
    ax.set_xlim((0, workspace.width))
    ax.set_ylim((0, workspace.length))
    plt.xticks(np.arange(0, workspace.width + 1, 5))
    plt.yticks(np.arange(0, workspace.length + 1, 5))
    plot_workspace_helper(ax, workspace.regions, 'region')
    plot_workspace_helper(ax, workspace.obstacles, 'obstacle')
    # plt.grid(visible=True, which='major', color='gray', linestyle='--')
    plt.savefig('./data/supermarket.png', format='png', dpi=300)

    # plt.title(r'$\phi_3$')


def plot_workspace_helper(ax, obj, obj_label):
    plt.rc('text', usetex=False)
    plt.rc('font', family='serif')
    plt.gca().set_aspect('equal', adjustable='box')
    # p0 dock
    # p1 grocery p2 health p3 outdors p4 pet p5 furniture p6 electronics 
    # p7 packing area
    region = {'p0': 'dock',
            'p1': 'grocery',
            'p2': 'health',
            'p3': 'outdoor',
            'p4': 'pet supplies',
            'p5': 'furniture',
            'p6': 'electronics',
            'p7': 'packing area'}
    for key in obj:
        if 'r' in key:
            continue
        # color = 'gray' if obj_label != 'region' else 'white'
        color = 'gray' if obj_label != 'region' or (key == 'p0' or key == 'p7') else 'green'
        alpha = 0.6 if obj_label != 'region' or (key == 'p0' or key == 'p7') else 0.1
        for grid in obj[key]:
            x_ = grid[0]
            y_ = grid[1]
            x = []
            y = []
            patches = []
            for point in [(x_, y_), (x_ + 1, y_), (x_ + 1, y_ + 1), (x_, y_ + 1)]:
                x.append(point[0])
                y.append(point[1])
            polygon = Polygon(np.column_stack((x, y)), True)
            patches.append(polygon)
            p = PatchCollection(patches, facecolors=color, edgecolors=color, linewidths=0.2, alpha=alpha)
            ax.add_collection(p)
        # ax.text(np.mean(x) - 0.2, np.mean(y) - 0.2, r'${}_{{{}}}$'.format(key[0], key[1:]), fontsize=12)
        if key == 'p0':
            ax.text(np.mean(x) + 1, np.mean(y) - 5, r'{}'.format(region[key]), fontsize=6)
        elif key == 'p7':
            ax.text(np.mean(x) - 3.5, np.mean(y) + 1, r'{}'.format(region[key]), fontsize=6)
        elif 'o' in key:
            ax.text(np.mean(x) - 2, np.mean(y) + 1, r'{}'.format(region['p' + key[1:]]), fontsize=6)



def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
 
 
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
 
 
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
 
 
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
 
 
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
 
 
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
 
 
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
 
 
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))
 