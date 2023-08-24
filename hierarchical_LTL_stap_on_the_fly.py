import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from specification import Specification
from buchi import BuchiConstructor
from util import create_parser, vis_graph, plot_workspace, prGreen, prRed, prYellow
from workspace_supermarket import Workspace
from product_ts import ProductTs
import networkx as nx 
from itertools import product
from dijkstra_on_the_fly import multi_source_multi_targets_dijkstra
import matplotlib.pyplot as plt
from vis import vis
from data_structure import Node

import time
from collections import namedtuple
Hierarchy = namedtuple('Hierarchy', ['level', 'phi', 'buchi_graph', 'decomp_sets'])
    
def get_locations_for_buchi_state(workspace, buchi_graph, buchi_state):
    # @TODO consider various capabilities of robots
    target_aps = set() # target ap that enable the transition to buchi_state
    target_cells = []
    for prec in buchi_graph.pred[buchi_state]:
        # get ap that enable the transition to accept node
        target_aps.update(BuchiConstructor.get_positive_literals(buchi_graph.edges[(prec, buchi_state)]['label']))  
    for target_ap in target_aps:
        target_cells.extend(workspace.regions[target_ap])
    return target_cells

def main(args=None):
    parser = create_parser()
    args = parser.parse_known_args()[0]
    start_time = time.time() # Record the start time
   
    # ==========================
    # Step 1: spec
    # ==========================
    specs = Specification()
    specs.get_task_specification(task=args.task, case=args.case)
    hierarchy_graph = specs.build_hierarchy_graph(args.vis)
    leaf_specs = [node for node in hierarchy_graph.nodes() if hierarchy_graph.out_degree(node) == 0]
    print(specs.hierarchy)
    spec_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate {} specs".format(spec_time - start_time, hierarchy_graph.number_of_nodes()))
    
    # ==========================
    # Step 2: buichi graph and decomposition sets
    # ==========================
    buchi_constructor = BuchiConstructor()
    task_hierarchy = dict()
    for index, level in enumerate(specs.hierarchy):
        for (phi, spec) in level.items():
            buchi_graph = buchi_constructor.construct_buchi_graph(spec)
            decomp_sets = None
            if phi in leaf_specs:
                decomp_sets = buchi_constructor.get_all_decomp_nodes(buchi_graph=buchi_graph)
            task_hierarchy[phi] = Hierarchy(level=index+1, phi=phi, buchi_graph=buchi_graph, decomp_sets=decomp_sets)
    buchi_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate buchi graph".format(buchi_time - spec_time))
    prRed("Buchi graph for {} has {} nodes and {} edges, with decomp sets {}".format(list(task_hierarchy.keys()), 
                                                                [h.buchi_graph.number_of_nodes() for h in task_hierarchy.values()],
                                                                [h.buchi_graph.number_of_edges() for h in task_hierarchy.values()],
                                                                [h.decomp_sets for h in task_hierarchy.values()],))

    # print(task_hierarchy.items())
    if args.vis:
        for phi, h in task_hierarchy.items():
            vis_graph(h.buchi_graph, f'data/{phi}', latex=False, buchi_graph=True)
            
    # ==========================
    # Step 3: workspace
    # ==========================
    workspace = Workspace()
    if args.vis:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plot_workspace(workspace, ax)
        vis_graph(workspace.graph_workspace, f'data/workspace', latex=False, buchi_graph=False)
    workspace_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate workspace".format(workspace_time - buchi_time))    
    prRed(f"Worksapce has {workspace.graph_workspace.number_of_nodes()} nodes and {workspace.graph_workspace.number_of_edges()} edges")

                    
    # ==========================
    # Step 4: search on the fly
    # ==========================
    sources = []
    for phi in leaf_specs:
        for q in task_hierarchy[phi].buchi_graph.graph['init']:
            type_robots_x = workspace.type_robot_location.copy()
            leaf_phis = {phi: task_hierarchy[phi].buchi_graph.graph['init'][0] for phi in leaf_specs}
            leaf_phis[phi] = q
            type_robot = list(workspace.type_robot_location.keys())[0]
            sources.append(Node(phi, type_robot, type_robots_x[type_robot], q, type_robots_x, leaf_phis))         
    # prRed(f'init nodes:  {init_nodes}')
    # prRed(f'number of target nodes: {phi_target_nodes}')
    ProductTs.essential_type_robot_x = set([(type_robot, x) for type_robot, x in workspace.type_robot_location.items()])
    _, optimal_path = multi_source_multi_targets_dijkstra(sources, task_hierarchy, workspace, 
                                                          {'p100': ['p200'], 'p200': ['p300'], 'p300': []})
                                                        #   leaf_spec_order={leaf_spec: [] for leaf_spec in leaf_specs})
    search_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to search".format(search_time - workspace_time))
    # prRed(f'optimal path {optimal_path}')
    
    # ==========================
    # Step 8: extract robot path
    # ========================== 
    robot_path = {type_robot: [] for type_robot in workspace.type_robot_location.keys() }
    pre_phi = ''
    for wpt in optimal_path:
        if pre_phi and wpt.phi != pre_phi:
            for robot, path in robot_path.items():
                if not path:
                    path.append(workspace.type_robot_location[robot])
            horizon = max([len(path) for path in robot_path.values()])
            for path in robot_path.values():
                path.extend((horizon - len(path)) * [path[-1]])
                # prRed(path)
        
        # prYellow(wpt)
        pre_phi = wpt.phi
        type_robot = wpt.type_robot
        x = wpt.x
        robot_path[type_robot].append(x)

    horizon = max([len(path) for path in robot_path.values()])
    for path in robot_path.values():
        path.extend((horizon - len(path)) * [path[-1]])
        # prRed(path)
    path_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to extract path".format(path_time - search_time))
    if args.vis:
        vis(args.task, args.case, workspace, robot_path, {robot: [len(path)] * 2 for robot, path in robot_path.items()}, [])
        vis_time = time.time() # Record the end time
        prGreen("Take {:.2f} secs to visualize".format(vis_time - search_time))
        
        
if __builtins__:
    main()