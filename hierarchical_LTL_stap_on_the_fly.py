from hierarchical_ltl_stap.specification import Specification
from hierarchical_ltl_stap.buchi import BuchiConstructor
from hierarchical_ltl_stap.util import create_parser, vis_graph, plot_workspace, prGreen, prRed, prYellow, depth_to_leaf

from hierarchical_ltl_stap.product_ts import ProductTs
import networkx as nx 
from itertools import product
from hierarchical_ltl_stap.dijkstra_on_the_fly import multi_source_multi_targets_dijkstra
import matplotlib.pyplot as plt
from hierarchical_ltl_stap.vis import vis
from hierarchical_ltl_stap.data_structure import Node, SpecInfo
from hierarchical_ltl_stap.task_network import construct_task_network
from hierarchical_ltl_stap.execution import generate_simultaneous_exec, eventExec

import time

def main(args=None):
    parser = create_parser()
    args = parser.parse_known_args()[0]
    if args.domain == "supermarket":
        from hierarchical_ltl_stap.workspace_supermarket import Workspace
    elif args.domain == "bosch":
        from hierarchical_ltl_stap.workspace_bosch import Workspace
    elif args.domain == "ai2thor":
        from hierarchical_ltl_stap.workspace_ai2thor import Workspace

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
        depth = depth_to_leaf(hierarchy_graph, spec)
        if depth in depth_specs.keys():
            depth_specs[depth].append(spec)
        else:
            depth_specs[depth] = [spec]
    depth_specs = {k: depth_specs[k] for k in sorted(depth_specs)}
    path_to_root = dict()
    for spec in leaf_specs:
        path_to_root[spec] = nx.shortest_path(hierarchy_graph, source="p0", target=spec)[::-1]
    # specs_with_increasing_depth = []
    # for key in sorted(depth_specs.keys()):
    #     specs_with_increasing_depth.extend(depth_specs[key])
    if args.print_step:    
        prRed(f"Specs: {specs.hierarchy}")
        prRed(f"Depth: {depth_specs}")
        prRed(f"Path to root: {path_to_root}")
        spec_time = time.time() # Record the end time
        prGreen("Take {:.2f} secs to generate {} specs".format(spec_time - start_time, hierarchy_graph.number_of_nodes()))
    
    # ==========================
    # Step 2: workspace
    # ==========================
    if args.domain == "supermarket" or args.domain == "bosch":
        workspace = Workspace(args.domain_file, args.num_robots)
    elif args.domain == "ai2thor":
        leaf_specs_ltl = [specs.hierarchy[-1][leaf_spec] for leaf_spec in leaf_specs]
        workspace = Workspace(leaf_specs_ltl, args.num_robots)
    if args.vis:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plot_workspace(workspace, ax)
        vis_graph(workspace.graph_workspace, f'data/workspace', latex=False, buchi_graph=False)
    workspace_time = time.time() # Record the end time
    if args.print_step:    
        prGreen("Take {:.2f} secs to generate workspace".format(workspace_time - spec_time))    
        prRed(f"Workspace has {workspace.graph_workspace.number_of_nodes()} nodes and {workspace.graph_workspace.number_of_edges()} edges")
                   

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
    task_hierarchy, leaf_spec_order, first_spec_candidates = construct_task_network(specs, leaf_specs, workspace, args)
    buchi_time = time.time() # Record the end time
    if args.print_step:    
        prGreen("Take {:.2f} secs to generate buchi graph".format(buchi_time - workspace_time))
        prRed("Buchi graph for {} has {} nodes and {} edges, with decomp sets {}".format(list(task_hierarchy.keys()), 
                                                                [h.buchi_graph.number_of_nodes() for h in task_hierarchy.values()],
                                                                [h.buchi_graph.number_of_edges() for h in task_hierarchy.values()],
                                                                [h.decomp_sets for h in task_hierarchy.values()],))
        prRed(f"First spec candidates: {first_spec_candidates}")
        prRed(f"Order between leaf specs: {leaf_spec_order}")
    
    spec_info = SpecInfo(depth_specs=depth_specs, path_to_root=path_to_root,
                         leaf_spec_order=leaf_spec_order)

    # print(task_hierarchy.items())
    if args.vis:
        for phi, h in task_hierarchy.items():
            vis_graph(h.buchi_graph, f'data/{phi}', latex=False, buchi_graph=True)
                              
    # ==========================
    # Step 4: search on the fly
    # ==========================
    #sources are from specs that can be the first one to be finished
    sources = []
    all_inits = [list(task_hierarchy[phi].buchi_graph.graph['init']) for phi in task_hierarchy.keys()]
    prod_inits = [list(item) for item in product(*all_inits)]
    for first_phi in first_spec_candidates:
        for init in prod_inits:
            phis_progress = {phi: init[idx] for idx, phi in enumerate(task_hierarchy.keys())}
            type_robots_x = workspace.type_robot_location.copy()
            type_robot = list(workspace.type_robot_location.keys())[0]
            sources.append(Node(first_phi, type_robot, 'default', 'x', type_robots_x, phis_progress, set(), 
                                ProductTs.update_progress_metric(task_hierarchy, phis_progress), dict()))  
        
    # phis_progress = {phi: tuple(task_hierarchy[phi].buchi_graph.graph['init']) for phi in task_hierarchy.keys()}
    # for phi in first_spec_candidates:
    #     for q in task_hierarchy[phi].buchi_graph.graph['init']:
    #         type_robots_x = workspace.type_robot_location.copy()
    #         phis_progress.copy()
    #         phis_progress[phi] = q
    #         type_robot = list(workspace.type_robot_location.keys())[0]
    #         sources.append(Node(phi, type_robot, type_robots_x, phis_progress))         
    # prRed(f'init nodes:  {init_nodes}')
    # prRed(f'number of target nodes: {phi_target_nodes}')
    ProductTs.essential_phi_type_robot_x = set([(phi, type_robot, x, q) for phi in leaf_specs
                                                for q in set(task_hierarchy[phi].buchi_graph.graph['init']) | \
                                                    set(task_hierarchy[phi].buchi_graph.graph['accept']) | \
                                                        set(task_hierarchy[phi].decomp_sets) 
                                                for type_robot, x in workspace.type_robot_location.items()])
    cost, optimal_path = multi_source_multi_targets_dijkstra(sources, task_hierarchy, workspace, spec_info, args)
    search_time = time.time() # Record the end time
    if args.print_step:    
        prGreen("Take {:.2f} secs to search".format(search_time - buchi_time))

    # ==========================
    # Step 5: extract robot path
    # ========================== 
    robot_path, robot_phi, robot_act = generate_simultaneous_exec(optimal_path, workspace, leaf_spec_order, args)
    # prRed(robot_act)
    if args.print_step:    
        path_time = time.time() # Record the end time
        prGreen("Take {:.2f} secs to extract path".format(path_time - search_time))
    prGreen("The path cost {:.2f}".format(cost))
    if args.event:
        eventExec(robot_path, robot_phi, robot_act, leaf_spec_order, first_spec_candidates)
        # event_based_execution(robot_path, robot_phi, robot_act, leaf_spec_order, first_spec_candidates)
    if args.vis:
        vis(args.task, args.case, workspace, robot_path, {robot: [len(path)] * 2 for robot, path in robot_path.items()}, [], robot_act)
        vis_time = time.time() # Record the end time
        prGreen("Take {:.2f} secs to visualize".format(vis_time - search_time))
        
        
if __builtins__:
    main()