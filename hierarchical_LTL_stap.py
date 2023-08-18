import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from specification import Specification
from buchi import BuchiConstructor
from util import create_parser, vis_graph
from workspace_supermarket import Workspace
from product_ts import ProductTs
import networkx as nx 
from itertools import product

from collections import namedtuple
Hierarchy = namedtuple('Hierarchy', ['level', 'phi', 'buchi_graph', 'decomp_sets'])

def main(args=None):
    parser = create_parser()
    args = parser.parse_known_args()[0]
    # spec
    specs = Specification()
    specs.get_task_specification(task=args.task, case=args.case)
    hierarchy_graph = specs.build_hierarchy_graph(args.vis)
    leaf_specs = [node for node in hierarchy_graph.nodes() if hierarchy_graph.out_degree(node) == 0]
    print(specs.hierarchy)
    
    # buichi graph and decomposition sets
    buchi_constructor = BuchiConstructor()
    task_hierarchy = dict()
    for index, level in enumerate(specs.hierarchy):
        for (phi, spec) in level.items():
            buchi_graph = buchi_constructor.construct_buchi_graph(spec)
            decomp_sets = None
            if phi in leaf_specs:
                decomp_sets = buchi_constructor.get_all_decomp_nodes(buchi_graph=buchi_graph)
            task_hierarchy[phi] = Hierarchy(level=index+1, phi=phi, buchi_graph=buchi_graph, decomp_sets=decomp_sets)
    # print(task_hierarchy.items())
    if args.vis:
        for phi, h in task_hierarchy.items():
            vis_graph(h.buchi_graph, f'data/{phi}', latex=False, buchi_graph=True)
    
    # workspace
    workspace = Workspace()
    if args.vis:
        workspace.plot_workspace()
        vis_graph(workspace.graph_workspace, f'data/workspace', latex=False, buchi_graph=False)
        
    # team model
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
    if args.vis:
        for phi_type_robot, augmented_prod_ts in prod_ts_map.items():
            vis_graph(augmented_prod_ts, f'data/prod_ts_{phi_type_robot[0]}_{phi_type_robot[1][0]}_{phi_type_robot[1][1]}', latex=False, buchi_graph=False)

    print(prod_ts_map.keys())     
       
    # connect graphs between different agents for the same spec
    team_prod_ts = nx.DiGraph()
    type_robots = list(workspace.type_robot_location.keys())
    for leaf_spec in leaf_specs:
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
    if args.vis:
        vis_graph(team_prod_ts, f'data/team_prod_ts', latex=False)

    # connect graphs between different specs for the same agent

    init_node = [(leaf_spec, (1, 0), workspace.type_robot_location[(1, 0)], init) for leaf_spec in leaf_specs for init in task_hierarchy[leaf_spec].buchi_graph.graph['init']]
    target_nodes = [node for node in team_prod_ts.nodes() if 'accept' in node[-1]]
    print(init_node)
    
            
if __builtins__:
    main()