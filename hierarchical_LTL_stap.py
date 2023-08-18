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
import matplotlib.pyplot as plt
from vis import vis

import time
from collections import namedtuple
Hierarchy = namedtuple('Hierarchy', ['level', 'phi', 'buchi_graph', 'decomp_sets'])

def main(args=None):
    parser = create_parser()
    args = parser.parse_known_args()[0]
    start_time = time.time() # Record the start time
   
    # Step 1: spec
    specs = Specification()
    specs.get_task_specification(task=args.task, case=args.case)
    hierarchy_graph = specs.build_hierarchy_graph(args.vis)
    leaf_specs = [node for node in hierarchy_graph.nodes() if hierarchy_graph.out_degree(node) == 0]
    print(specs.hierarchy)
    spec_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate {} specs".format(spec_time - start_time, hierarchy_graph.number_of_nodes()))
    
    # Step 2: buichi graph and decomposition sets
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
    
    # Step 3: workspace
    workspace = Workspace()
    if args.vis:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plot_workspace(workspace, ax)
        vis_graph(workspace.graph_workspace, f'data/workspace', latex=False, buchi_graph=False)
    workspace_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate workspace".format(workspace_time - buchi_time))    
    prRed(f"Worksapce has {workspace.graph_workspace.number_of_nodes()} nodes and {workspace.graph_workspace.number_of_edges()} edges")
    
    # Step 4: team model
    prod_ts_constructor = ProductTs()
    prod_ts_map = dict()
    for phi, h in task_hierarchy.items():
        if phi not in leaf_specs:
            continue
        prod_ts = prod_ts_constructor.construct_ts(task_hierarchy[phi].buchi_graph, workspace)
        for type_robot in workspace.type_robot_label.keys():
            augmented_prod_ts = nx.DiGraph()
            for node in prod_ts.nodes():
                augmented_prod_ts.add_node((phi, type_robot) + node, label= (phi, type_robot) + node)
            for from_node, to_node, w in prod_ts.edges.data('weight', default=1):
                augmented_prod_ts.add_edge((phi, type_robot) + from_node, (phi, type_robot) + to_node, weight=w)
            prod_ts_map[(phi, type_robot)] = augmented_prod_ts
    prod_ts_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate product ts".format(prod_ts_time - workspace_time))    
    prRed("Product ts for {} has {} nodes and {} edges".format(list(prod_ts_map.keys()),
                                                    [graph.number_of_nodes() for graph in prod_ts_map.values()], 
                                                    [graph.number_of_edges() for graph in prod_ts_map.values()]))
    # if args.vis:
    #     for phi_type_robot, augmented_prod_ts in prod_ts_map.items():
    #         vis_graph(augmented_prod_ts, f'data/prod_ts_{phi_type_robot[0]}_{phi_type_robot[1][0]}_{phi_type_robot[1][1]}', latex=False, buchi_graph=False)
       
    # Step 5: connect graphs between different agents for the same spec
    team_prod_ts = nx.DiGraph()
    type_robots = list(workspace.type_robot_location.keys())
    for leaf_spec in leaf_specs:
        # prYellow(leaf_spec)
        hierarchy = task_hierarchy[leaf_spec]
        decomp_set = hierarchy.decomp_sets | set(hierarchy.buchi_graph.graph['init']) | set(hierarchy.buchi_graph.graph['accept'])
        prod_ts_spec_agents = [prod_ts_map[(leaf_spec, type_robot)] for type_robot in type_robots]
        for prod_ts_spec_agent in prod_ts_spec_agents:
            team_prod_ts.add_nodes_from(prod_ts_spec_agent.nodes(data=True))
            team_prod_ts.add_edges_from(prod_ts_spec_agent.edges(data=True)) 
        for idx in range(len(type_robots) - 1):
            from_type_robot = type_robots[idx]
            to_type_robot = type_robots[idx + 1]
            to_type_robot_init_location = workspace.type_robot_location[to_type_robot]
            for decomp_state in decomp_set:
                from_node = [(leaf_spec, from_type_robot) + (location, decomp_state) for location in workspace.graph_workspace.nodes()]
                to_node = (leaf_spec, to_type_robot) + (to_type_robot_init_location, decomp_state)
                team_prod_ts.add_edges_from(product(from_node, [to_node]), weight=0)
    team_prod_ts_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate team prod ts".format(team_prod_ts_time - prod_ts_time))
    # if args.vis:
    #     vis_graph(team_prod_ts, f'data/team_prod_ts', latex=False)

    # Step 6: connect graphs between different specs for the same agent
    # Step 7: search
    init_nodes = [(leaf_spec, (1, 0), workspace.type_robot_location[(1, 0)], init) \
        for leaf_spec in leaf_specs for init in task_hierarchy[leaf_spec].buchi_graph.graph['init']]
    target_nodes = []
    for phi, h in task_hierarchy.items():
        if phi not in leaf_specs:
            continue
        for accept_node in h.buchi_graph.graph['accept']:
            target_aps = set() # target ap that enable the transition to accept nodes
            target_cells = []
            for prec in h.buchi_graph.pred[accept_node]:
                # get ap that enable the transition to accept node
                target_aps.update(BuchiConstructor.get_positive_literals(h.buchi_graph.edges[(prec, accept_node)]['label']))  
            prYellow(target_aps)
            for target_ap in target_aps:
                target_cells.extend(workspace.regions[target_ap])
            for node in team_prod_ts.nodes():
                # @TODO consider various capabilities of robots
                if node[0] == phi and node[-1] == accept_node and node[2] in target_cells:
                    target_nodes.append(node)
            
    prRed(f'init nodes:  {init_nodes}')
    prRed(f'number of target nodes: {len(target_nodes)}')
    # @TODO too many target nodes
    optimal_cost = 1e10
    optimal_path = None
    for target_node in target_nodes:
        res = nx.algorithms.multi_source_dijkstra(team_prod_ts, init_nodes, target_node, weight='weight')
        if res[0] < optimal_cost:
            optimal_cost = res[0]
            optimal_path = res[1]
        # prRed(f'target_node: {target_node}, {res}')
    search_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to search".format(search_time - team_prod_ts_time))
    prRed(f'optimal path {optimal_path}')
    
    # Step 8: extract robot path 
    robot_path = {type_robot: [] for type_robot in workspace.type_robot_location.keys() }
    for wpt in optimal_path:
        robot_path[wpt[1]].append(wpt[2])
    for robot, path in robot_path.items():
        if not path:
            path.append(workspace.type_robot_location[robot])
    horizon = max([len(path) for path in robot_path.values()])
    for path in robot_path.values():
        path.extend((horizon - len(path)) * [path[-1]])
        prRed(path)
    path_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to extract path".format(path_time - search_time))
    if args.vis:
        vis(args.task, args.case, workspace, robot_path, {robot: [len(path)] * 2 for robot, path in robot_path.items()}, [])
        vis_time = time.time() # Record the end time
        prGreen("Take {:.2f} secs to visualize".format(vis_time - search_time))
if __builtins__:
    main()