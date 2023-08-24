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
from dijkstra import multi_source_multi_targets_dijkstra
import matplotlib.pyplot as plt
from vis import vis

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
    # Step 4: team model
    # ==========================
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
       
    # ==========================      
    # Step 5: connect graphs between different agents for the same spec
    # ==========================
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
            # loop from robot 1 to n
            from_type_robot = type_robots[idx]
            to_type_robot = type_robots[idx + 1]
            to_type_robot_init_location = workspace.type_robot_location[to_type_robot]
            for decomp_state in decomp_set:
                # connect target location leading to decomp state to init location of another robot
                target_locs = get_locations_for_buchi_state(workspace, hierarchy.buchi_graph, decomp_state)
                from_node = [(leaf_spec, from_type_robot) + (loc, decomp_state) for loc in target_locs]
                to_node = (leaf_spec, to_type_robot) + (to_type_robot_init_location, decomp_state)
                team_prod_ts.add_edges_from(product(from_node, [to_node]), weight=0)
    team_prod_ts_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to generate team prod ts".format(team_prod_ts_time - prod_ts_time))
    # if args.vis:
    #     vis_graph(team_prod_ts, f'data/team_prod_ts', latex=False)

    # ==========================
    # Step 6: connect graphs between different specs for the same agent
    # 6.1 for the same robot, connect from one init node of a team model to the init node of another team model with init location
    # ==========================
    for type_robot in type_robots:
        type_robot_init_location = workspace.type_robot_location[type_robot]
        for from_leaf_spec, to_leaf_spec in product(leaf_specs, leaf_specs): # refine according to temporal order between specs
            if from_leaf_spec == to_leaf_spec:
                continue
            from_buchi_graph = task_hierarchy[from_leaf_spec].buchi_graph
            to_buchi_graph = task_hierarchy[to_leaf_spec].buchi_graph
            from_node = [(from_leaf_spec, type_robot) + (type_robot_init_location, init_node) 
                         for init_node in from_buchi_graph.graph['init']]
            to_node = [(to_leaf_spec, type_robot) + (type_robot_init_location, init_node) 
                         for init_node in to_buchi_graph.graph['init']]
            team_prod_ts.add_edges_from(product(from_node, to_node), weight=0)
            prYellow(list(product(from_node, to_node)))
            
    # 6.2 for the same robot, connect from one accept node of a team model to every init node of another team model with target location
    for type_robot in type_robots:
        for from_leaf_spec, to_leaf_spec in product(leaf_specs, leaf_specs):
            if from_leaf_spec == to_leaf_spec:
                continue
            from_buchi_graph = task_hierarchy[from_leaf_spec].buchi_graph
            to_buchi_graph = task_hierarchy[to_leaf_spec].buchi_graph
            type_robot_init_location = workspace.type_robot_location[type_robot]
            for accept_node in from_buchi_graph.graph['accept']:
                target_locs = get_locations_for_buchi_state(workspace, from_buchi_graph, accept_node)
                for target_loc in target_locs:
                    from_node = [(from_leaf_spec, type_robot) + (target_loc, accept_node)]
                    to_node = [(to_leaf_spec, type_robot) + (target_loc, init_node) for init_node in to_buchi_graph.graph['init']]
                    team_prod_ts.add_edges_from(product(from_node, to_node), weight=0)
                    prYellow(list(product(from_node, to_node)))
                    
    # 6.3 for different robots, connect from one accept node of a team model to every init node of another team model with corresponding location                
    # TO BE IMPLEMENTED
    # for type_robot in type_robots:
    #     for from_leaf_spec, to_leaf_spec in product(leaf_specs, leaf_specs):
    #         if from_leaf_spec == to_leaf_spec:
    #             continue
    #         from_buchi_graph = task_hierarchy[from_leaf_spec].buchi_graph
    #         to_buchi_graph = task_hierarchy[to_leaf_spec].buchi_graph
    #         type_robot_init_location = workspace.type_robot_location[type_robot]
    #         for decomp_node in task_hierarchy[from_leaf_spec].decomp_set:
    #             target_locs = get_locations_for_buchi_state(workspace, from_buchi_graph, decomp_node)
    #             for target_loc in target_locs:
    #                 from_node = [(from_leaf_spec, type_robot) + (target_loc, decomp_node)]
    #                 to_node = [(to_leaf_spec, type_robot) + (target_loc, init_node) for init_node in to_buchi_graph.graph['init']]
    #                 team_prod_ts.add_edges_from(product(from_node, to_node), weight=0)
    #                 prYellow(list(product(from_node, to_node)))                
                    
    # ==========================
    # Step 7: search
    # ==========================
    init_nodes = [(leaf_spec, (1, 0), workspace.type_robot_location[(1, 0)], init) \
        for leaf_spec in leaf_specs for init in task_hierarchy[leaf_spec].buchi_graph.graph['init']]
    
    phi_target_nodes = {leaf_spec : [] for leaf_spec in leaf_specs}
    for phi, h in task_hierarchy.items():
        if phi not in leaf_specs:
            continue
        for accept_node in h.buchi_graph.graph['accept']:
            target_locs = get_locations_for_buchi_state(workspace, h.buchi_graph, accept_node)
            phi_target_nodes[phi] = [(phi, (1, 0), loc, accept_node) for loc in target_locs]
            
    prRed(f'init nodes:  {init_nodes}')
    prRed(f'number of target nodes: {phi_target_nodes}')
    _, optimal_path = multi_source_multi_targets_dijkstra(team_prod_ts, init_nodes, set(leaf_specs), weight='weight')
    search_time = time.time() # Record the end time
    prGreen("Take {:.2f} secs to search".format(search_time - team_prod_ts_time))
    # prRed(f'optimal path {optimal_path}')
    
    # ==========================
    # Step 8: extract robot path
    # ========================== 
    robot_path = {type_robot: [] for type_robot in workspace.type_robot_location.keys() }
    for wpt, _ in optimal_path:
        _, type_robot, loc, _ = wpt
        robot_path[type_robot].append(loc)
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