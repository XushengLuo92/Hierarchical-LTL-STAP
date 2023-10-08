import networkx as nx 
import subprocess
import argparse
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np 

import networkx as nx

def depth_to_leaf(G, start_node):
    """Find the length of the longest path from start_node to any leaf."""
    
    # Helper recursive function
    def dfs(node, visited):
        visited.add(node)
        
        if G.out_degree(node) == 0:  # leaf node
            return 0
        
        max_depth = 0
        for neighbor in G.successors(node):
            if neighbor not in visited:
                depth = dfs(neighbor, visited)
                max_depth = max(max_depth, depth + 1)
        
        return max_depth

    return dfs(start_node, set())

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
    parser.add_argument('--print', action='store_true', help='Enable print to terminal')
    parser.add_argument('--log', action='store_true', help='Enable save log')
    parser.add_argument('--dot', action='store_true', help='Enable dot graph')
    parser.add_argument('--simul', action='store_true', help='Enable simultaneous execution')
    parser.add_argument('--event', action='store_true', help='Enable event based execution')
    parser.add_argument('--domain_file', default="./src/domain_default.json")
    parser.add_argument('--heuristic_weight', default=0, type=int)
    parser.add_argument('--domain', default="supermarket", type=str)
    return parser

def plot_workspace(workspace, ax):
    if workspace.name() == "supermarket":
        plot_supermarket(workspace, ax)
    elif workspace.name() == "bosch":
        plot_bosch(workspace, ax)
        
def plot_supermarket(workspace, ax):
    plt.rc('text', usetex=False)
    ax.set_xlim((0, workspace.width))
    ax.set_ylim((0, workspace.height))
    plt.xticks(np.arange(0, workspace.width + 1, 5))
    plt.yticks(np.arange(0, workspace.height + 1, 5))
    plot_supermarket_helper(ax, workspace.regions, 'region')
    plot_supermarket_helper(ax, workspace.obstacles, 'obstacle')
    # plt.grid(visible=True, which='major', color='gray', linestyle='--')
    plt.savefig('./data/supermarket.png', format='png', dpi=300)

def plot_bosch(workspace, ax):
    plt.rc('text', usetex=False)
    ax.set_xlim((1, workspace.width))
    ax.set_ylim((1, workspace.height))
    plt.xticks(np.arange(1, workspace.width + 1, 5))
    plt.yticks(np.arange(1, workspace.height + 1, 5))
    plot_bosch_helper(ax, workspace.regions, 'region')
    plot_bosch_helper(ax, workspace.obstacles, 'obstacle')
    # plt.grid(visible=True, which='major', color='gray', linestyle='--')
    plt.savefig('./data/bosch_building.png', format='png', dpi=300)

def plot_supermarket_helper(ax, obj, obj_label):
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
            
def plot_bosch_helper(ax, obj, obj_label):
    plt.rc('text', usetex=False)
    plt.rc('font', family='serif')
    plt.gca().set_aspect('equal', adjustable='box')
 
    for key in obj:
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
        if 'obs' not in key and 'r' not in key:
            ax.text(np.mean(x)-0.4, np.mean(y)-0.2, key, fontsize=6)
        # if 'obs' not in key and 'r' in key:
        #     ax.text(np.mean(x)-0.4, np.mean(y)-0.2, key, fontsize=12)
        

def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
 
 
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
 
 
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
 
 
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
 
 
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
 
 
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
 
 
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
 
 
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))

def print_partial_order(pruned_subgraph, hasse_graph, element2edge):
    _, poset_relation, _, _ = hasse_graph
    for order in poset_relation:
        print("pairwise order: ", pruned_subgraph.edges[element2edge[order[0]]]['label'], ' -> ',
                pruned_subgraph.edges[element2edge[order[1]]]['label'], "           subtasks: ", element2edge[order[0]],
                element2edge[order[1]])

def print_primitive_subtasks(pruned_subgraph, element2edge, primitive_subtasks):
    for primitive_subtask in primitive_subtasks:
        edge = element2edge[primitive_subtask]
        print("primitive element {2}, subtask: {0}, label: {1}".format(edge, pruned_subgraph.edges[edge]["label"], primitive_subtask))

def print_composite_subtasks(pruned_subgraph, element2edge, composite_subtasks_dict):
    for (subtask, elements) in composite_subtasks_dict.items():
        for element in elements:
            print("composite subtask {0}, element {1}, label {2}".format(subtask, element, pruned_subgraph.edges[element2edge[element]]["label"]))

def print_subtask_info(task_hierarchy, leaf_specs, primitive_subtasks, composite_subtasks):
    for (task, hierarchy) in task_hierarchy.items():
        if task in leaf_specs:
            continue
        prCyan(">>>>>> level {0} task {1}, formula {2}".format(hierarchy.level, task, hierarchy.phi))
        print_partial_order(hierarchy.buchi_graph, hierarchy.hass_graph, hierarchy.element2edge)
        print_primitive_subtasks(hierarchy.buchi_graph, hierarchy.element2edge, primitive_subtasks[task].element_in_poset)
        print_composite_subtasks(hierarchy.buchi_graph, hierarchy.element2edge, composite_subtasks[task].subtask2element)
        
def print_primitive_subtasks_with_identifer(primitive_subtasks_with_identifer, task_hierarchy):
     # print all primitive subtasks with identifier
    print("************* all primitive subtasks **************")
    for ele in primitive_subtasks_with_identifer:
        element2edge = task_hierarchy[ele.parent].element2edge
        buchi_graph = task_hierarchy[ele.parent].buchi_graph
        print("parent {0}, element {1}, edge {2}, label {3}".format(ele.parent, ele.element, element2edge[ele.element], 
                                                                    buchi_graph.edges[element2edge[ele.element]]['label']))
        
def print_global_partial_order(primitive_subtasks_partial_order, task_hierarchy):
    print("************* partial order between primitive subtasks **************")
    for partial_order in primitive_subtasks_partial_order:
        pre = partial_order[0]
        suc = partial_order[1]
        pre_element2edge = task_hierarchy[pre.parent].element2edge
        pre_buchi_graph = task_hierarchy[pre.parent].buchi_graph
        suc_element2edge = task_hierarchy[suc.parent].element2edge
        suc_buchi_graph = task_hierarchy[suc.parent].buchi_graph
        print("parent {0}, element {1}, edge {2}, label {3} -> parent {4}, element {5}, edge {6}, label {7}".\
            format(pre.parent, pre.element, pre_element2edge[pre.element], pre_buchi_graph.edges[pre_element2edge[pre.element]]['label'],
                   suc.parent, suc.element, suc_element2edge[suc.element], suc_buchi_graph.edges[suc_element2edge[suc.element]]['label']))
      
            