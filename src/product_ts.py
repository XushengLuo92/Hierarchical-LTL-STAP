
from itertools import product
import networkx as nx
from sympy import symbols
from buchi import BuchiConstructor
from data_structure import Node
from workspace_supermarket import Workspace

class ProductTs(object):
    essential_phi_type_robot_x = set()
    
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
    
    @staticmethod
    def update_phis_progress(phis_progress, task_hierarchy, depth_specs):
        # print(phis_progress)
        phis_truth = dict()
        for depth, specs in depth_specs.items():
            if depth == 0:
                for spec in specs:
                    if 'accept' in phis_progress[spec]:
                        phis_truth[symbols(spec)] = True
                    else:
                        phis_truth[symbols(spec)] = False
                continue
            for spec in specs:
                q_progress = set()
                buchi_graph = task_hierarchy[spec].buchi_graph
                for q in phis_progress[spec]:
                    for next_q in buchi_graph.succ[q]:
                        edge_label = buchi_graph.edges[(q, next_q)]['label']
                        if edge_label.subs(phis_truth):
                            q_progress.add(next_q)
                    node_label = buchi_graph.nodes[q]['label']
                    if node_label.subs(phis_truth):
                            q_progress.add(q)
                phis_progress[spec] = tuple(q_progress)
                for q in phis_progress[spec]:
                    if 'accept' in q:
                        phis_truth[symbols(spec)] = True
                        break
                    else:
                        phis_truth[symbols(spec)] = False

    @staticmethod
    # find successors for the same agent and same spec
    def produce_succ_inside_ps(node: Node, task_hierarchy, workspace: Workspace, spec_info):
        leaf_specs = spec_info.leaf_spec_order.keys()
        depth_specs = spec_info.depth_specs
        path_to_root = spec_info.path_to_root
        
        # return if the accepting state has been reached, no need to search inside the ps for the same robot
        # unless accepting state is violated
        for parent in path_to_root[node.phi]:
            parent_buchi_graph = task_hierarchy[parent].buchi_graph
            if node.phis_progress[parent] in parent_buchi_graph.graph['accept']:
                return []
            
        succ = []
        buchi_graph = task_hierarchy[node.phi].buchi_graph
        x = node.type_robots_x[node.type_robot]
        q = node.phis_progress[node.phi]
        decomp_set = task_hierarchy[node.phi].decomp_sets
        aps_true = symbols(workspace.get_atomic_prop(x))
        next_xs = list(workspace.graph_workspace.neighbors(x))  # next_xs includes x
        node_label = buchi_graph.nodes[q]['label']
        aps_in_label = BuchiConstructor.get_literals(node_label)
        aps_sub = {ap: True if ap in aps_true else False for ap in symbols(aps_in_label)}
        type_robots_x = set(node.type_robots_x.values())
        if node_label.subs(aps_sub) == True:
            for next_x in next_xs:
                # self-loop
                if x != next_x and next_x in type_robots_x: # collision avoidance
                    continue
                updated_type_robots_x = node.type_robots_x.copy()
                updated_type_robots_x[node.type_robot] = next_x
                weight = 0 if x == next_x else 1
                succ.append([Node(node.phi, node.type_robot, updated_type_robots_x, node.phis_progress), weight])
               
        next_qs = buchi_graph.succ[q]
        for next_q in next_qs:
            edge_label = buchi_graph.edges[(q, next_q)]['label']
            aps_in_label = BuchiConstructor.get_literals(edge_label)
            aps_sub = {ap: True if ap in aps_true else False for ap in symbols(aps_in_label)}
            if edge_label.subs(aps_sub) == True:    
                # update progress of leaf phis if accepting state or decomp state is reached
                updated_phis_progress = node.phis_progress.copy()
                updated_phis_progress[node.phi] = next_q
                # update progress of other parent specs 
                ProductTs.update_phis_progress(updated_phis_progress, task_hierarchy, depth_specs)
                if next_q in buchi_graph.graph['accept'] or next_q in decomp_set:
                    for next_x in next_xs:
                        if x != next_x and next_x in type_robots_x:
                            continue
                        updated_type_robots_x = node.type_robots_x.copy()
                        updated_type_robots_x[node.type_robot] = next_x
                        weight = 0 if x == next_x else 1
                        succ.append([Node(node.phi, node.type_robot, updated_type_robots_x, updated_phis_progress), weight])
                        # update essentail x of type_robot
                        if x == next_x and q != next_q:
                            # NOTE consider transition (phi_1, r, x, q_1) -> (phi_2, r, x, q_2) -> (phi_2, r', x', q_2)
                            ProductTs.essential_phi_type_robot_x.update({(phi, node.type_robot, x, q) for phi in leaf_specs
                                                for q in set(task_hierarchy[phi].buchi_graph.graph['init']) | \
                                                    set(task_hierarchy[phi].buchi_graph.graph['accept']) | \
                                                        set(task_hierarchy[phi].decomp_sets)})
                else:
                    for next_x in next_xs:
                        if x != next_x and next_x in type_robots_x:
                            continue
                        updated_type_robots_x = node.type_robots_x.copy()
                        updated_type_robots_x[node.type_robot] = next_x
                        weight = 0 if x == next_x else 1
                        succ.append([Node(node.phi, node.type_robot, updated_type_robots_x, updated_phis_progress), weight])
        return succ
    
    @staticmethod
    def get_locations_for_buchi_state(workspace: Workspace, buchi_graph: nx.DiGraph, buchi_state):
        # @TODO consider various capabilities of robots
        target_aps = set() # target ap that enable the transition to buchi_state
        target_cells = []
        for prec in buchi_graph.pred[buchi_state]:
            # get ap that enable the transition to accept node
            target_aps.update(BuchiConstructor.get_positive_literals(buchi_graph.edges[(prec, buchi_state)]['label']))  
        for target_ap in target_aps:
            target_cells.extend(workspace.regions[target_ap])
        return target_cells

    @staticmethod
    # find successor with decomp sets for the same spec between consecutive robots
    def produce_succ_between_ps_same_phi(node:Node, task_hierarchy, workspace: Workspace, path_to_root):
        # return if the accepting state has been reached, no need to search inside the ps for the same robot
        for parent in path_to_root[node.phi]:
            parent_buchi_graph = task_hierarchy[parent].buchi_graph
            if node.phis_progress[parent] in parent_buchi_graph.graph['accept']:
                return []
            
        type_robots = list(workspace.type_robot_location.keys())
        # prYellow(leaf_spec)
        hierarchy = task_hierarchy[node.phi]
        decomp_set = hierarchy.decomp_sets | set(hierarchy.buchi_graph.graph['init']) | set(hierarchy.buchi_graph.graph['accept'])
        # q is not a decomp state
        q = node.phis_progress[node.phi]
        if q not in decomp_set:
            return []
        # robot is the last one
        idx = type_robots.index(node.type_robot)
        if idx == len(type_robots) - 1:
            return []
        next_type_robot = type_robots[idx + 1]
        # x is not in desired areas that lead to decomp state; different from IJRR paper
        if (node.phi, node.type_robot, node.type_robots_x[node.type_robot], node.phis_progress[node.phi]) not in ProductTs.essential_phi_type_robot_x or \
        (node.phi, next_type_robot, node.type_robots_x[next_type_robot], node.phis_progress[node.phi]) not in ProductTs.essential_phi_type_robot_x:
            return []
        # if node.q not in hierarchy.buchi_graph.graph['init']:
        #     desired_x = ProductTs.get_locations_for_buchi_state(workspace, hierarchy.buchi_graph, node.q)
        #     if node.x not in desired_x and node.x != node.type_robots_x[node.type_robot]:
        #         return []
        succ = [Node(node.phi, next_type_robot, node.type_robots_x, node.phis_progress), 0]
        return [succ]
    
    def produce_succ_between_ps_same_robot(node: Node, task_hierarchy, workspace: Workspace, leaf_phis_order):
        succ = []
        buchi_graph = task_hierarchy[node.phi].buchi_graph
        x = node.type_robots_x[node.type_robot]
        q = node.phis_progress[node.phi]
        # @TODO It seems no need to connect init with init
        # # for the same robot, connect from one init node of a team model to the init node of another team model with init location
        # if q in buchi_graph.graph['init'] and (node.type_robot, x) in ProductTs.essential_type_robot_x:
        #     # update buchi state
        #     for leaf_phi in leaf_phis_order[node.phi]:
        #         leaf_buchi_graph = task_hierarchy[leaf_phi].buchi_graph
        #         for q in leaf_buchi_graph.graph['init']:
        #             updated_phis_progress = node.phis_progress.copy()
        #             updated_phis_progress[leaf_phi] = q
        #             succ.append([Node(leaf_phi, node.type_robot, node.type_robots_x, updated_phis_progress), 0])
        
        # in case of precedence relation, only connect accept to init
        # in case of independence relation, connect all decomp states except init to init   
        # for the same robot, connect from one accept node of a team model to every init node of another team model with target location
        if q in buchi_graph.graph['accept'] and (node.phi, node.type_robot, x, q) in ProductTs.essential_phi_type_robot_x:
            # constrain the set of states that can be accepting product states
            # update buchi state
            for leaf_phi in leaf_phis_order[node.phi]: # only connect when precedence relation exists
                leaf_buchi_graph = task_hierarchy[leaf_phi].buchi_graph
                leaf_q = node.phis_progress[leaf_phi]
                if leaf_q in leaf_buchi_graph.graph['init'] and \
                    (leaf_phi, node.type_robot, x, node.phis_progress[leaf_phi]) in ProductTs.essential_phi_type_robot_x:
                    succ.append([Node(leaf_phi, node.type_robot, node.type_robots_x, node.phis_progress), 0])

        # for the same robot, if two phis are independent, connect from one decomp node of a team model to the current decomp node (if so) of another team model
        hierarchy = task_hierarchy[node.phi]   
        if (q in hierarchy.decomp_sets or q in buchi_graph.graph['accept'] ) and \
            (node.phi, node.type_robot, x, q) in ProductTs.essential_phi_type_robot_x:
            for leaf_phi in leaf_phis_order[node.phi]:
                if node.phi in leaf_phis_order[leaf_phi]:
                    leaf_buchi_graph = task_hierarchy[leaf_phi].buchi_graph
                    leaf_q = node.phis_progress[leaf_phi]
                    leaf_hierarchy = task_hierarchy[leaf_phi]
                    if leaf_q in (leaf_hierarchy.decomp_sets | set(leaf_hierarchy.buchi_graph.graph['init'])) and \
                        (leaf_phi, node.type_robot, node.type_robots_x[node.type_robot], node.phis_progress[leaf_phi]) in ProductTs.essential_phi_type_robot_x:
                        succ.append([Node(leaf_phi, node.type_robot, node.type_robots_x, node.phis_progress), 0])
            
        # connect from its accept node of a team model to every init node of the first robot's team model with corresponding location                
        type_robots = list(workspace.type_robot_location.keys())
        if q in buchi_graph.graph['accept'] and (node.phi, node.type_robot, x, q) in ProductTs.essential_phi_type_robot_x:
                # constrain the set of states that can be accepting product states
                # update buchi state
                for leaf_phi in leaf_phis_order[node.phi]:
                    leaf_buchi_graph = task_hierarchy[leaf_phi].buchi_graph
                    leaf_q = node.phis_progress[leaf_phi]
                    if leaf_q in leaf_buchi_graph.graph['init'] and \
                        (leaf_phi, type_robots[0], node.type_robots_x[type_robots[0]], node.phis_progress[leaf_phi]) in ProductTs.essential_phi_type_robot_x:
                        succ.append([Node(leaf_phi, type_robots[0], node.type_robots_x, node.phis_progress), 0])
        return succ
    
    @staticmethod
    def produce_succ(node: Node, task_hierarchy, workspace: Workspace, spec_info):
        return ProductTs.produce_succ_inside_ps(node, task_hierarchy, workspace, spec_info)  + \
            ProductTs.produce_succ_between_ps_same_phi(node, task_hierarchy, workspace, spec_info.path_to_root) + \
                ProductTs.produce_succ_between_ps_same_robot(node, task_hierarchy, workspace, spec_info.leaf_spec_order)