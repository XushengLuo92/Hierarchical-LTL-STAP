from .data_structure import Hierarchy, PrimitiveSubtask, CompositeSubtask, PrimitiveSubtaskId
from .buchi import BuchiConstructor
from .util import print_subtask_info, print_global_partial_order, \
    print_primitive_subtasks_with_identifer, vis_graph, prCyan, prRed
from collections import namedtuple
import networkx as nx
from sympy import to_dnf
import os
from itertools import product
from .workspace_supermarket import Workspace
    
def is_primitive(label, leaf_specs):
    # task is primitive if exist literal with "location" smaller than 100
    if label != to_dnf('1'):
        aps = BuchiConstructor.get_literals(label)
        for ap in aps:
            is_primitive = ap in leaf_specs
            if is_primitive:
                return True
    return False

def get_primitive_and_composite_subtask(pruned_subgraph, element2edge, leaf_specs):
    primitive_elements = set()
    composite_elements = set()
    composite_subtask_element_dict = dict()
    for element in element2edge:
        task_label = pruned_subgraph.edges[element2edge[element]]['label']
        if is_primitive(task_label, leaf_specs):
            primitive_elements.add(element)
        elif task_label != to_dnf("1"):
            composite_elements.add(element)
            pos_ap = BuchiConstructor.get_positive_literals(task_label)
            for ap in pos_ap:
                if ap not in composite_subtask_element_dict.keys():
                    composite_subtask_element_dict[ap] = [element]
                else:
                    composite_subtask_element_dict[ap].append(element)

    return primitive_elements, composite_elements, composite_subtask_element_dict

def build_buchi_graph_and_poset(task_specification, leaf_specs, workspace: Workspace, args):
    primitive_subtasks = dict()
    composite_subtasks = dict()
    task_hierarchy = dict()
    
    buchi_constructor = BuchiConstructor()
    task_hierarchy = dict()
    nodes = []
    edges = []
    for index, level in enumerate(task_specification.hierarchy):
        for (phi, spec) in level.items():
            buchi_graph = buchi_constructor.construct_buchi_graph(spec)
            if phi in leaf_specs:
                buchi_graph.graph['conflict_aps'] = list(workspace.regions.keys())
            else:
                buchi_graph.graph['conflict_aps'] = list(task_specification.hierarchy[index+1].keys())
            decomp_sets = None
            if args.print_task:
                prCyan(f"{phi}, {spec}, {buchi_graph.number_of_nodes()} nodes and {buchi_graph.number_of_edges()} edge")
            nodes.append(buchi_graph.number_of_nodes())
            edges.append(buchi_graph.number_of_edges())
            # find decomp nodes for leaf specs
            if phi in leaf_specs:
                # decomp_sets do not include init and accept in the implementation
                buchi_constructor.prune_graph(buchi_graph)
                buchi_constructor.prune_clauses(buchi_graph)
                # print(buchi_graph.number_of_nodes(), buchi_graph.number_of_edges())
                decomp_sets = BuchiConstructor.get_decomp_set_stap(buchi_graph)
                # prCyan(f'decomp: {decomp_sets}')
                # decomp_sets = buchi_constructor.get_all_decomp_nodes(buchi_graph)
                buchi_constructor.get_dist_to_init_states(buchi_graph)
                # buchi_graph has been pruned in get_all_decomp_nodes
                task_hierarchy[phi] = Hierarchy(level=index+1, phi=spec, buchi_graph=buchi_graph, decomp_sets=decomp_sets,
                                                 hass_graph=hasse_graph, element2edge=element2edge)
            else:
                pruned_subgraph, hasse_graph, element2edge = buchi_constructor.get_ordered_subtasks(buchi_graph)
                buchi_constructor.get_dist_to_init_states(pruned_subgraph)
                task_hierarchy[phi] = Hierarchy(level=index+1, phi=spec, buchi_graph=pruned_subgraph, decomp_sets=decomp_sets,
                                                hass_graph=hasse_graph, element2edge=element2edge)
                primitive_elements, composite_element, composite_subtask_element_dict = \
                    get_primitive_and_composite_subtask(pruned_subgraph, element2edge, leaf_specs)
                primitive_subtasks[phi] = PrimitiveSubtask(element_in_poset=primitive_elements)
                composite_subtasks[phi] = CompositeSubtask(subtask2element=composite_subtask_element_dict)
            if args.print_task:
                prRed(f"{task_hierarchy[phi].buchi_graph.graph['formula']}, {task_hierarchy[phi].buchi_graph.graph['dist']}")
    if args.print_task:
        prCyan(f"total nodes {sum(nodes)}, edges {sum(edges)}")
    # buchi_time = time.time() # Record the end time
    # prGreen("Take {:.2f} secs to generate buchi graph".format(buchi_time - spec_time))
    # prRed("Buchi graph for {} has {} nodes and {} edges, with decomp sets {}".format(list(task_hierarchy.keys()), 
    #                                                             [h.buchi_graph.number_of_nodes() for h in task_hierarchy.values()],
    #                                                             [h.buchi_graph.number_of_edges() for h in task_hierarchy.values()],
    #                                                             [h.decomp_sets for h in task_hierarchy.values()],))



    return task_hierarchy, primitive_subtasks, composite_subtasks

def produce_global_poset_within_composite_subtask(task_hierarchy, leaf_specs, primitive_subtasks, vis=False):
    primitive_subtasks_partial_order = []
    for (task, hierarchy) in task_hierarchy.items():
        if task in leaf_specs:
            continue
        buchi_graph = hierarchy.buchi_graph
        element2edge = hierarchy.element2edge
        hass_graph = hierarchy.hass_graph #  [(w, h), {edge for edge in hasse.edges()}, list(hasse.nodes), hasse]
        poset_relation = hass_graph[1]
        primitive_elements = hass_graph[2] # only check prilimitive elements appearing in the specific poset
        checked_primitive_pairs = []
        for ele_a in primitive_elements:
            for ele_b in primitive_elements:
                if ele_a == ele_b or ((ele_a, ele_b) in checked_primitive_pairs or (ele_b, ele_a) in checked_primitive_pairs):
                    continue
                checked_primitive_pairs.append((ele_a, ele_b))
                if (ele_a, ele_b) in poset_relation:
                    primitive_subtasks_partial_order.append((PrimitiveSubtaskId(parent=task, element=ele_a), PrimitiveSubtaskId(parent=task, element=ele_b)))
                    if vis:
                        print("within composite subtask {0} element: {1} -> {2} label: {3} -> {4}".\
                            format(task, ele_a, ele_b, buchi_graph.edges[element2edge[ele_a]]["label"],\
                                buchi_graph.edges[element2edge[ele_b]]["label"]))
                elif (ele_a, ele_b) in poset_relation:
                    primitive_subtasks_partial_order.append((PrimitiveSubtaskId(parent=task, element=ele_b), PrimitiveSubtaskId(parent=task, element=ele_a)))
                    if vis:
                        print("within composite subtask {0} element: {1} -> {2} label: {3} -> {4}".\
                            format(task, ele_b, ele_a, buchi_graph.edges[element2edge[ele_b]]["label"],\
                                buchi_graph.edges[element2edge[ele_a]]["label"]))
                else:
                    if vis:
                        print("within composite subtask {0} element: {1} || {2} label: {3} || {4}".\
                            format(task, ele_a, ele_b, buchi_graph.edges[element2edge[ele_a]]["label"],\
                                buchi_graph.edges[element2edge[ele_b]]["label"]))
    return primitive_subtasks_partial_order

def get_task_seq(target_task, task_hierarchy, composite_subtasks):
    task_seq = [target_task]
    level = task_hierarchy[target_task].level
    while level > 1:
        for (task, hierarchy) in task_hierarchy.items():
            if hierarchy.level == level - 1 and task_seq[-1] in hierarchy.buchi_graph.graph['formula']:
                task_seq.append(task)
                level = level - 1
                break
    return task_seq
            
def find_shared_element(vector1, vector2):
    for element in vector1:
        if element in vector2:
            return element
    return None  # No shared element found

def produce_global_poset_from_composite_subtask_pair(task_hierarchy, leaf_specs, composite_subtasks, primitive_subtasks, vis=False):
    # get the smallest common ancestor of any two composite subtasks
    Parents = namedtuple('Parents', ['parent_front', 'parent_back', 'common_parent'])
    composite_subtask_pair_with_parent = dict()
    for task_a in task_hierarchy.keys():
        if task_a in leaf_specs:
            continue
        task_a_seq = get_task_seq(task_a, task_hierarchy, composite_subtasks)
        for task_b in task_hierarchy.keys():
            if task_b in leaf_specs:
                continue
            if task_a == task_b or ((task_a, task_b) in composite_subtask_pair_with_parent.keys() or 
                                        (task_b, task_a) in composite_subtask_pair_with_parent.keys()):
                continue
            task_b_seq = get_task_seq(task_b, task_hierarchy, composite_subtasks)
            parent = find_shared_element(task_a_seq, task_b_seq)
            assert(parent != None)
            task_a_parent_index = max(1, task_a_seq.index(parent))
            task_b_parent_index = max(1, task_b_seq.index(parent))
            # if parent == task_a or parent == task_b:
            #     continue
            composite_subtask_pair_with_parent[(task_a, task_b)] = Parents(parent_front=task_a_seq[task_a_parent_index-1],
                                                                            parent_back=task_b_seq[task_b_parent_index-1],
                                                                            common_parent=parent)
    if vis:
        for (subtask_pair, parents) in composite_subtask_pair_with_parent.items():
            print("subtask {0} {1}, parent {2} {3}, common {4}".format(subtask_pair[0], subtask_pair[1], \
                parents.parent_front, parents.parent_back, parents.common_parent))
    # get partial order based on composite tasks
    primitive_subtasks_partial_order = []
    for (subtask_pair, parents) in composite_subtask_pair_with_parent.items():
        hass_graph = task_hierarchy[parents.common_parent].hass_graph
        poset_relation = hass_graph[1]
        buchi_graph = task_hierarchy[parents.common_parent].buchi_graph
        element2edge =task_hierarchy[parents.common_parent].element2edge
        one_is_parent_of_the_other = subtask_pair[0] == parents.common_parent or subtask_pair[1] == parents.common_parent
        # if ont task is not the parent of the other task, then loop over all combinations of primitive subtasks
        if not one_is_parent_of_the_other:
            composite_subtask_element_dict = composite_subtasks[parents.common_parent]
            parent_element_from_pair0 = composite_subtask_element_dict.subtask2element[parents.parent_front][0]
            parent_element_from_pair1 = composite_subtask_element_dict.subtask2element[parents.parent_back][0]
            # all child tasks of a task inherit the parital order w.r.t. all child tasks of a nother task
            if (parent_element_from_pair0, parent_element_from_pair1) in poset_relation:
                primitive_subtasks_partial_order.extend([(PrimitiveSubtaskId(parent=subtask_pair[0], element=pre), PrimitiveSubtaskId(parent=subtask_pair[1], element=suc)) \
                for pre in primitive_subtasks[subtask_pair[0]].element_in_poset for suc in primitive_subtasks[subtask_pair[1]].element_in_poset])
                if vis:
                    print("[composite subtask {0} -> {1},  parent {2} {3} common {4}] parent element: {5} -> {6} parent label: {7} -> {8}".\
                        format(subtask_pair[0], subtask_pair[1], parents.parent_front, parents.parent_back, parents.common_parent, \
                            parent_element_from_pair0, parent_element_from_pair1, buchi_graph.edges[element2edge[parent_element_from_pair0]]["label"],\
                            buchi_graph.edges[element2edge[parent_element_from_pair1]]["label"]))
            elif (parent_element_from_pair1, parent_element_from_pair0) in poset_relation:
                primitive_subtasks_partial_order.extend([(PrimitiveSubtaskId(parent=subtask_pair[1], element=pre), PrimitiveSubtaskId(parent=subtask_pair[0], element=suc)) \
                for pre in primitive_subtasks[subtask_pair[1]].element_in_poset for suc in primitive_subtasks[subtask_pair[0]].element_in_poset])
                if vis:
                    print("[composite subtask {0} -> {1}, parent {2} {3} common {4}] parent element: {5} -> {6} parent label: {7} -> {8}".\
                        format(subtask_pair[1], subtask_pair[0], parents.parent_back, parents.parent_front, parents.common_parent, \
                            parent_element_from_pair1, parent_element_from_pair0, buchi_graph.edges[element2edge[parent_element_from_pair1]]["label"],\
                            buchi_graph.edges[element2edge[parent_element_from_pair0]]["label"]))
            else:
                if vis:
                    print("[composite subtask {0} || {1}, parent {2} {3} common {4}] parent element: {5} || {6} parent label: {7} || {8}".\
                        format(subtask_pair[0], subtask_pair[1], parents.parent_front, parents.parent_back, parents.common_parent,\
                            parent_element_from_pair0, parent_element_from_pair1, buchi_graph.edges[element2edge[parent_element_from_pair0]]["label"],\
                            buchi_graph.edges[element2edge[parent_element_from_pair1]]["label"]))
        # if one task is the parent of the other task, then got the primitive subtasks of parent and composite subtask of child
        else:
            child = subtask_pair[0]
            parent_of_child = parents.parent_front
            if parents.common_parent == subtask_pair[0]:
                child = subtask_pair[1]
                parent_of_child = parents.parent_back
            for primitive_element in primitive_subtasks[parents.common_parent].element_in_poset:
                composite_element = composite_subtasks[parents.common_parent].subtask2element[parent_of_child][0]
                # all child tasks of a task inherit the parital order w.r.t. all child tasks of another task
                if (primitive_element, composite_element) in poset_relation:
                    primitive_subtasks_partial_order.extend([(PrimitiveSubtaskId(parent=parents.common_parent, element=primitive_element), PrimitiveSubtaskId(parent=child, element=suc)) \
                    for suc in primitive_subtasks[child].element_in_poset])
                    if vis:
                        print("[comp subtask {0}, parent {1} common {2}] parent element: {3} -> {4} parent label: {5} -> {6}".\
                            format(child, parent_of_child, parents.common_parent, primitive_element, composite_element, \
                                buchi_graph.edges[element2edge[primitive_element]]["label"],\
                                buchi_graph.edges[element2edge[composite_element]]["label"]))
                elif (composite_element, primitive_element) in poset_relation:
                    primitive_subtasks_partial_order.extend([(PrimitiveSubtaskId(parent=child, element=pre), PrimitiveSubtaskId(parent=parents.common_parent, element=primitive_element)) \
                    for pre in primitive_subtasks[child].element_in_poset])
                    if vis:
                        print("[comp subtask {0}, parent {1} common {2}] parent element: {3} -> {4} parent label: {5} -> {6}".\
                            format(child, parent_of_child, parents.common_parent, composite_element, primitive_element, \
                                buchi_graph.edges[element2edge[composite_element]]["label"],\
                                buchi_graph.edges[element2edge[primitive_element]]["label"]))
                else:
                    if vis:
                        print("[comp subtask {0}, parent {1} common {2}] parent element: {3} || {4} parent label: {5} || {6}".\
                            format(child, parent_of_child, parents.common_parent, primitive_element, composite_element, \
                                buchi_graph.edges[element2edge[primitive_element]]["label"],\
                                buchi_graph.edges[element2edge[composite_element]]["label"]))
    return primitive_subtasks_partial_order

def produce_global_poset(task_hierarchy, leaf_specs, composite_subtasks, primitive_subtasks, vis=False, dot=False):
    # get partial order within single composite task
    primitive_subtasks_partial_order = produce_global_poset_within_composite_subtask(task_hierarchy, leaf_specs, primitive_subtasks, vis)
    # get partial order between composite tasks
    primitive_subtasks_partial_order.extend(produce_global_poset_from_composite_subtask_pair(task_hierarchy, leaf_specs, composite_subtasks, primitive_subtasks, vis))
    # # get partial order from composite subtask with primitive subtask in the first level
    # primitive_subtasks_partial_order.extend(produce_global_poset_from_composite_and_primitive_subtasks(task_hierarchy, composite_subtasks, primitive_subtasks))
    primitive_subtasks_with_identifier = []
    for task in task_hierarchy.keys():
        if task in leaf_specs:
            continue
        for primitive_subtask in primitive_subtasks[task].element_in_poset:
            primitive_subtasks_with_identifier.append(PrimitiveSubtaskId(parent=task, element=primitive_subtask))
    return primitive_subtasks_with_identifier, primitive_subtasks_partial_order

def generate_global_poset_graph(task_hierarchy, primitive_subtasks_with_identifier, primitive_subtasks_partial_order):
    task_network = nx.DiGraph(type='TaskNetwork')
    for task in primitive_subtasks_with_identifier:
        buchi_graph  = task_hierarchy[task.parent].buchi_graph
        edge = task_hierarchy[task.parent].element2edge[task.element]
        label = buchi_graph.edges[edge]['label']
        task_network.add_node((task.parent, task.element), label=label)
    
    for pair in primitive_subtasks_partial_order:
        task_network.add_edge((pair[0].parent, pair[0].element), (pair[1].parent, pair[1].element))

    reduced_task_network = nx.transitive_reduction(task_network)
    reduced_task_network.add_nodes_from(task_network.nodes(data=True))
    reduced_task_network.add_edges_from((u, v, task_network.edges[u, v]) for u, v in reduced_task_network.edges)
    return reduced_task_network

def construct_task_network(task_specification, leaf_specs, workspace: Workspace, args):
    task_hierarchy, primitive_subtasks, composite_subtasks = build_buchi_graph_and_poset(task_specification, leaf_specs, workspace, args)
    if args.print_task:
        print_subtask_info(task_hierarchy, leaf_specs, primitive_subtasks, composite_subtasks)
    # ----------------- partial global order set -----------------
    primitive_subtasks_with_identifier, primitive_subtasks_partial_order = produce_global_poset(task_hierarchy, leaf_specs, composite_subtasks, primitive_subtasks, args.print_task)
    if args.print_task:
        print_primitive_subtasks_with_identifer(primitive_subtasks_with_identifier, task_hierarchy)
        print_global_partial_order(primitive_subtasks_partial_order, task_hierarchy)
    reduced_task_network = generate_global_poset_graph(task_hierarchy, primitive_subtasks_with_identifier, primitive_subtasks_partial_order)
    reduced_task_network.graph["task"] = args.task
    dirname = os.path.dirname(__file__)
    if args.dot:
        semantic_reduced_task_network = reduced_task_network.copy()
        for task in primitive_subtasks_with_identifier:
            buchi_graph  = task_hierarchy[task.parent].buchi_graph
            edge = task_hierarchy[task.parent].element2edge[task.element]
            semantic_reduced_task_network.add_edge((task.parent, task.element), ((task.parent, task.element)), label=buchi_graph.nodes[edge[0]]['label'])
            # semantic_reduced_task_network.edges[(task.parent, task.element), ((task.parent, task.element))]['label'] = \
            # generate_latex_expr(buchi_graph.nodes[edge[0]]['label'], args.task, args.case) 
        vis_graph(semantic_reduced_task_network, dirname + '/../data/task_network', False, False)
    else:
        vis_graph(reduced_task_network, dirname + '/../data/task_network', False, False)
    
    leaf_spec_network = nx.DiGraph()
    leaf_spec_network.add_nodes_from(leaf_specs)
    for pre, succ in reduced_task_network.edges():
        pre_hierarchy = task_hierarchy[pre[0]]
        pre_edge_label = pre_hierarchy.buchi_graph.edges[pre_hierarchy.element2edge[pre[1]]]['label']
        pre_pos_literal = BuchiConstructor.get_positive_literals(pre_edge_label)
        succ_hierarchy = task_hierarchy[succ[0]]
        succ_edge_label = succ_hierarchy.buchi_graph.edges[succ_hierarchy.element2edge[succ[1]]]['label']
        succ_pos_literal = BuchiConstructor.get_positive_literals(succ_edge_label)
        for pre_literal, succ_literal in product(pre_pos_literal, succ_pos_literal):
            leaf_spec_network.add_edge(pre_literal, succ_literal)
            
    leaf_spec_order = {leaf_spec: [] for leaf_spec in leaf_specs}
    first_spec_candidates = []
    for leaf_spec_a in leaf_specs:
        # 1. Nodes reachable from the given node
        reachable_from_node = set(nx.descendants(leaf_spec_network, leaf_spec_a))
        # 2. Nodes from which the given node is reachable
        reachable_to_node = set(nx.ancestors(leaf_spec_network, leaf_spec_a))
        if not reachable_to_node:
            first_spec_candidates.append(leaf_spec_a)
        # 3. Combine the two sets
        all_connected_nodes = reachable_from_node.union(reachable_to_node)
        # 4. Subtract from the set of all nodes to get non-reachable nodes
        non_reachable_nodes = set(leaf_spec_network.nodes()) - all_connected_nodes - {leaf_spec_a}
        leaf_spec_order[leaf_spec_a] = reachable_from_node.union(non_reachable_nodes)

    use_heuristics = args.heuristics or args.heuristics_order
    if not use_heuristics:
        leaf_spec_order = {leaf_spec: set(leaf_specs) - {leaf_spec} for leaf_spec in leaf_specs}
        first_spec_candidates = leaf_specs
    return task_hierarchy, leaf_spec_order, first_spec_candidates