import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from specification import Specification
from buchi import BuchiConstructor
from util import create_parser, vis_graph, plot_workspace, prGreen, prRed, prYellow, longest_path_to_leaf
from workspace_supermarket import Workspace
from product_ts import ProductTs
import networkx as nx 
from itertools import product
from dijkstra_on_the_fly import multi_source_multi_targets_dijkstra
import matplotlib.pyplot as plt
from vis import vis
from data_structure import Node
from task_network import construct_task_network

import time

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
    non_leaf_specs = [node for node in hierarchy_graph.nodes() if node not in leaf_specs]
    depth_specs = {}
    for spec in hierarchy_graph.nodes():
        depth = longest_path_to_leaf(hierarchy_graph, spec)
        if depth in depth_specs.keys():
            depth_specs[depth].append(spec)
        else:
            depth_specs[depth] = [spec]
    depth_specs = {k: depth_specs[k] for k in sorted(depth_specs)}
    # specs_with_increasing_depth = []
    # for key in sorted(depth_specs.keys()):
    #     specs_with_increasing_depth.extend(depth_specs[key])    
    prRed(f"Specs: {specs.hierarchy}")
    prRed(f"Depth: {depth_specs}")
    spec_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate {} specs".format(spec_time - start_time, hierarchy_graph.number_of_nodes()))
    
    # ==========================
    # Step 2: workspace
    # ==========================
    workspace = Workspace()
    if args.vis:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plot_workspace(workspace, ax)
        vis_graph(workspace.graph_workspace, f'data/workspace', latex=False, buchi_graph=False)
    workspace_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate workspace".format(workspace_time - spec_time))    
    prRed(f"Worksapce has {workspace.graph_workspace.number_of_nodes()} nodes and {workspace.graph_workspace.number_of_edges()} edges")
                   

    # ==========================
    # Step 3: buichi graph, decomposition sets and posets
    # ==========================
    # buchi_constructor = BuchiConstructor()
    # task_hierarchy = dict()
    # for index, level in enumerate(specs.hierarchy):
    #     for (phi, spec) in level.items():
    #         buchi_graph = buchi_constructor.construct_buchi_graph(spec)
    #         decomp_sets = None
    #         if phi in leaf_specs:
    #             init_acpt = buchi_constructor.get_init_accept(buchi_graph)
    #             decomp_sets = buchi_constructor.get_all_decomp_nodes(buchi_graph, init_acpt)
    #         task_hierarchy[phi] = Hierarchy(level=index+1, phi=phi, buchi_graph=buchi_graph, decomp_sets=decomp_sets)
    task_hierarchy, leaf_spec_order = construct_task_network(specs, leaf_specs, workspace, args)
    buchi_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate buchi graph".format(buchi_time - workspace_time))
    prRed("Buchi graph for {} has {} nodes and {} edges, with decomp sets {}".format(list(task_hierarchy.keys()), 
                                                                [h.buchi_graph.number_of_nodes() for h in task_hierarchy.values()],
                                                                [h.buchi_graph.number_of_edges() for h in task_hierarchy.values()],
                                                                [h.decomp_sets for h in task_hierarchy.values()],))
    prRed(f"Order between leaf specs: {leaf_spec_order}")

    # print(task_hierarchy.items())
    if args.vis:
        for phi, h in task_hierarchy.items():
            vis_graph(h.buchi_graph, f'data/{phi}', latex=False, buchi_graph=True)
                              
    # ==========================
    # Step 4: search on the fly
    # ==========================
    # @TODO sources should be specs that can be the first one to be finished
    sources = []
    phis_progress = {phi: tuple(task_hierarchy[phi].buchi_graph.graph['init']) for phi in task_hierarchy.keys()}
    for phi in leaf_specs:
        for q in task_hierarchy[phi].buchi_graph.graph['init']:
            type_robots_x = workspace.type_robot_location.copy()
            phis_progress.copy()
            phis_progress[phi] = q
            type_robot = list(workspace.type_robot_location.keys())[0]
            sources.append(Node(phi, type_robot, type_robots_x, phis_progress))         
    # prRed(f'init nodes:  {init_nodes}')
    # prRed(f'number of target nodes: {phi_target_nodes}')
    ProductTs.essential_phi_type_robot_x = set([(phi, type_robot, x, q) for phi in leaf_specs
                                                for q in set(task_hierarchy[phi].buchi_graph.graph['init']) | \
                                                    set(task_hierarchy[phi].buchi_graph.graph['accept']) | \
                                                        set(task_hierarchy[phi].decomp_sets) 
                                                for type_robot, x in workspace.type_robot_location.items()])
    _, optimal_path = multi_source_multi_targets_dijkstra(sources, task_hierarchy, workspace, leaf_spec_order, depth_specs)
    search_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to search".format(search_time - buchi_time))
    # prRed(f'optimal path {optimal_path}')
    
    # ==========================
    # Step 5: extract robot path
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
        x = wpt.type_robots_x[type_robot]
        robot_path[type_robot].append(x)

    horizon = max([len(path) for path in robot_path.values()])
    for robot, path in robot_path.items():
        if not path:
            path.extend((horizon - len(path)) * [workspace.type_robot_location[robot]])
        else:
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