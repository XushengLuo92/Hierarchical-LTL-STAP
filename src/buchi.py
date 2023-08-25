import os
import subprocess
import re
from sympy.logic.boolalg import to_dnf, And, Or, Not
import networkx as nx
import numpy as np

class BuchiConstructor(object):
    """_summary_

    Args:
        object (_type_): _description_
    """
    def __init__(self) -> None:
        pass
    
    def construct_buchi_graph(self, formula):
        """
        parse the output of the program ltl2ba and build the buchi automaton
        """
        buchi_graph = nx.DiGraph(name="buchi graph", formula=formula)

        # directory of the program ltl2ba
        dirname = os.path.dirname(__file__)
        # output of the program ltl2ba
        output = subprocess.check_output(dirname + "/./../ltl2ba -f \"" + formula + "\"", shell=True).decode(
            "utf-8")
        # find all states/nodes in the buchi automaton
        state_re = re.compile(r'\n(\w+):\n\t')
        state_group = re.findall(state_re, output)
        # find initial and accepting states
        init = [s for s in state_group if 'init' in s]
        # treat the node accept_init as init node
        accept = [s for s in state_group if 'accept' in s]
        # finish the inilization of the graph of the buchi automaton
        buchi_graph.graph['init'] = init
        buchi_graph.graph['accept'] = accept
        # print("state %d, edge %d" % (len(state_group), output.count("::")))
        # for each state/node, find it transition relations
        for state in state_group:
            # add node
            buchi_graph.add_node(state, label=to_dnf('0'), name=state)
            # loop over all transitions starting from current state
            state_if_fi = re.findall(state + r':\n\tif(.*?)fi', output, re.DOTALL)
            if state_if_fi:
                relation_group = re.findall(r':: (\(.*?\)) -> goto (\w+)\n\t', state_if_fi[0])
                for symbol, next_state in relation_group:
                    symbol = symbol.replace('||', '|').replace('&&', '&').replace('!', '~')
                    formula = to_dnf(symbol)
                    # @TODO prune
                    # update node, do not create edges for selfloop
                    if state == next_state:
                        buchi_graph.nodes[state]['label'] = formula
                    else:
                        buchi_graph.add_edge(state, next_state, label=formula)
                        # print(buchi_graph.edges[(state, next_state)])

            else:
                state_skip = re.findall(state + r':\n\tskip\n', output, re.DOTALL)
                if state_skip:
                    buchi_graph.nodes[state]['label'] = to_dnf('1')
                    
        # delete vertices without selfloop
        self.delete_node_no_selfloop_except_init_accept(buchi_graph)
        
        return buchi_graph
    
    def delete_node_no_selfloop_except_init_accept(self, buchi_graph):
        """
        delete vertices without selfloop
        """
        remove_node = []
        for node in buchi_graph.nodes():
            # if no selfloop
            if not buchi_graph.nodes[node]['label']:
                # delete if not init or accept
                if 'init' not in node and 'accept' not in node:
                    remove_node.append(node)

        buchi_graph.remove_nodes_from(remove_node)
        
    def get_init_accept(self, buchi_graph):
        """
        search the shortest path from a node to another, i.e., # of transitions in the path, then sort
        """
        init_accept = dict()
        # shortest simple path for each init vertex to accept vertex
        for init in buchi_graph.graph['init']:
            init_graph = buchi_graph.copy()
            # remove all other initial vertices
            init_graph.remove_nodes_from([node for node in buchi_graph.graph['init'] if node != init])
            
            # iterate over all accepting vertices
            for accept in buchi_graph.graph['accept']:
                init_accept_graph = init_graph.copy()
                # remove all other accepting vertices except it is the exact init, 'accept_init'
                init_accept_graph.remove_nodes_from([node for node in buchi_graph.graph['accept']
                                                     if node != accept and node != init])
                # shortest simple path
                len1 = np.inf
                if init != accept:
                    try:
                        len1, _ = nx.algorithms.single_source_dijkstra(init_accept_graph,
                                                                       source=init, target=accept)
                    except nx.exception.NetworkXNoPath:
                        len1 = np.inf
                else:
                    for suc in init_accept_graph.succ[init]:
                        try:
                            length, path = nx.algorithms.single_source_dijkstra(init_accept_graph,
                                                                                source=suc, target=accept)
                        except nx.exception.NetworkXNoPath:
                            length, path = np.inf, []
                        if length + 1 < len1 and path:
                            len1 = length + 1
                # save
                init_accept[(init, accept)] = len1

        # shortest simple cycle, including self loop
        accept_accept = dict()
        for accept in buchi_graph.graph['accept']:
            # 0 if with self loop or without outgoing edges (co-safe formulae)
            if buchi_graph.nodes[accept]['label']:
                accept_accept[accept] = 0
                continue

            acpt_graph = buchi_graph.copy()
            # remove other accepting vertices
            acpt_graph.remove_nodes_from([node for node in buchi_graph.graph['accept'] if node != accept])

            # find the shortest path back to itself
            length = np.inf
            for suc in acpt_graph.succ[accept]:
                try:
                    len1, path = nx.algorithms.single_source_dijkstra(buchi_graph,
                                                                      source=suc, target=accept)
                except nx.exception.NetworkXNoPath:
                    len1, path = np.inf, []
                if len1 + 1 < length and path:
                    length = len1 + 1
            accept_accept[accept] = length

        # select initial to accept
        init_acpt = {pair: length + accept_accept[pair[1]] for pair, length in init_accept.items()
                     if length != np.inf and accept_accept[pair[1]] != np.inf}
        return sorted(init_acpt.items(), key=lambda x: x[1])
    
    def get_subgraph(self, init, accept, buchi_graph):
        """
        get the subgraph between init and accept
        """
        # (re)-initialize the set of edges that are satisfied by the initial locations
        self.sat_init_edge = []
        subgraph = buchi_graph.copy()
        # remove all other initial vertices for the prefix part
        subgraph.remove_nodes_from([node for node in buchi_graph.graph['init'] if node != init])
        if len(list(subgraph.succ[init])) == 0:
            raise RuntimeError('The task is infeasible!')
        # remove all other accepting vertices except it is the exact init, 'accept_init'
        subgraph.remove_nodes_from([node for node in buchi_graph.graph['accept']
                                    if node != accept and node != init])

        # node set
        nodes = self.find_all_nodes(subgraph, init, accept)
        subgraph = subgraph.subgraph(nodes).copy()
        subgraph.graph['init'] = (init, )
        subgraph.graph['accept'] = (accept, )

        # remove all outgoing edges of the accepting state from subgraph for the prefix part if head != tail
        if init != accept:
            remove_edge = list(subgraph.edges(accept))
            subgraph.remove_edges_from(remove_edge)
            
        # prune the subgraph
        removed_edge = self.prune_subgraph_automaton(subgraph)

        # get all paths in the pruned subgraph
        paths = []
        if init != accept:
            if subgraph.out_degree(init) == to_dnf('1') and subgraph.nodes[init]['label'] == to_dnf('0'):
                source = list(subgraph.succ[init])[0]
                paths = list(nx.all_simple_paths(subgraph, source=source, target=accept)) 
            else:
                paths = list(nx.all_simple_paths(subgraph, source=init, target=accept)) 
        else:
            for s in subgraph.succ[init]:
                paths = paths + [[init] + p for p in list(nx.all_simple_paths(subgraph, source=s, target=accept))]

        return subgraph, paths, removed_edge
    
    def prune_subgraph_automaton(self, subgraph):
        """
        prune the subgraph following ID and ST properties
        """
        removed_edge = []
        for node in subgraph.nodes():
            if 'init' in node and subgraph.nodes[node]['label'] == to_dnf('0'):
                for edge in subgraph.edges(node):
                    if subgraph.edges[edge]['label'] != to_dnf('1'):
                        removed_edge.append(edge)
        # remove the edge following ID and ST properties
        for node in subgraph.nodes():
            for succ in subgraph.succ[node]:
                if subgraph.nodes[node]['label'] == subgraph.nodes[succ]['label']:
                    for next_succ in subgraph.succ[succ]:
                        try:
                            # condition (c)
                            single_formula = subgraph.edges[(node, next_succ)]['label'] 
                            merge_formula = And(subgraph.edges[(node, succ)]['label'],
                                                subgraph.edges[(succ, next_succ)]['label'])
                            if single_formula.equals(merge_formula):
                                removed_edge.append((node, next_succ))
                        except KeyError:
                            continue
        
        for edge in subgraph.edges():
            if (subgraph.edges[edge]['label'] == to_dnf('1')):
                continue
            label = subgraph.edges[edge]['label']
            if isinstance(label, Or):           
                remain_clause = []
                for clause in label.args:
                    if len(set(BuchiConstructor.get_positive_literals(clause)).intersection(set(subgraph.graph['conflict_aps']))) <= 1:
                        remain_clause.append(clause)
                if len(remain_clause) == 0:
                    removed_edge.append(edge)
                else:
                    subgraph.edges[edge]['label'] = Or(*remain_clause)
            else:
                if len(set(BuchiConstructor.get_positive_literals(label)).intersection(set(subgraph.graph['conflict_aps']))) > 1:
                    # print(label, BuchiConstructor.get_positive_literals(label))
                    removed_edge.append(edge)
        
        subgraph.remove_edges_from(removed_edge)
                
        return removed_edge
        
    def find_all_nodes(self, subgraph, init, accept):
        """
        find all nodes that is some path that connects head and tail by finding all simple paths
        """
        in_between = {init, accept}
        if init != accept:
            for path in nx.all_simple_paths(subgraph, source=init, target=accept):
                in_between.update(set(path))
        else:
            for suc in subgraph.succ[init]:
                for path in nx.all_simple_paths(subgraph, source=suc, target=accept):
                    in_between.update(set(path))
        return in_between


    def get_element(self, pruned_subgraph):
        """
        map subtasks to integers
        """
        set_sets_edges = []
        # iterate over all edges and partition into set of sets of equivalent edges
        for edge_in_graph in pruned_subgraph.edges():
            is_added = False
            # iterate over each set of equivalent edges
            for set_edges in set_sets_edges:
                is_equivalent = True
                for edge in set_edges:
                    # equivalence: same node label and edge label, not in the same path
                    # when using sympy, == means structurally equivalent,
                    # it is OK here since we sort the literals in the clause
                    if pruned_subgraph.nodes[edge[0]]['label'] == pruned_subgraph.nodes[edge_in_graph[0]]['label'] \
                            and pruned_subgraph.edges[edge]['label'] == pruned_subgraph.edges[edge_in_graph][
                                'label'] \
                            and not (
                                nx.has_path(pruned_subgraph, edge_in_graph[1], edge[0]) or nx.has_path(pruned_subgraph,
                                                                                                       edge[1],
                                                                                                       edge_in_graph[
                                                                                                           0])):
                        continue
                    else:
                        # break if the considered edge edge_in_graph does not belong to this set of equivalent edges
                        is_equivalent = False
                        break
                # if belong to this set, add then mark
                if is_equivalent:
                    set_edges.append(edge_in_graph)
                    is_added = True
                    break
            # if not added, create a new set of equivalent edges
            if not is_added:
                set_sets_edges.append([edge_in_graph])

        # map each set of equivalent edges to one integer/element
        curr_element = 0
        edge2element = dict()
        element2edge = dict()
        for set_edges in set_sets_edges:
            curr_element += 1
            element2edge[curr_element] = set_edges[0]
            for edge in set_edges:
                edge2element[edge] = curr_element

        return edge2element, element2edge
    
    def prune_subgraph(self, subgraph):
        """
        remove the edge as long as there exists another path the connects the vertices
        """
        original_edges = list(subgraph.edges)
        for edge in original_edges:
            subgraph.remove_edge(edge[0], edge[1])
            if nx.has_path(subgraph, edge[0], edge[1]):
                continue
            else:
                subgraph.add_edge(edge[0], edge[1])
                
    def map_path_to_element_sequence(self, edge2element, paths):
        """
        map path to sequence of elements
        """
        element_sequences = []  # set of sets of paths sharing the same set of elements
        element_seq_to_path_map = dict()
        # put all path that share the same set of elements into one group
        for path in paths:
            element_sequence = []
            # map one path to one seq of integers
            for i in range(len(path) - 1):
                element_sequence.append(edge2element[(path[i], path[i + 1])])
            element_seq_to_path_map[tuple(element_sequence)] = path
            is_added = False
            for i in range(len(element_sequences)):
                # if the considered sequence of integers belong to this set of sequences of integers
                if set(element_sequences[i][0]) == set(element_sequence):
                    element_sequences[i].append(element_sequence)
                    is_added = True
                    break
            # create a new set of sequences of integers
            if not is_added:
                element_sequences.append([element_sequence])
        
        # for each set of sequences of integers, find one poset
        hasse_graphs = {}
        for index, ele_seq in enumerate(element_sequences):
            # all pairs of ordered elements from the sequence of elements
            linear_order = []
            for i in range(len(ele_seq[0])):
                for j in range(i + 1, len(ele_seq[0])):
                    linear_order.append((ele_seq[0][i], ele_seq[0][j]))
            # remove contradictive pairs by iterating over the remaining sequences of integers
            for i in range(1, len(ele_seq)):
                for j in range(len(ele_seq[1]) - 1):
                    if (ele_seq[i][j + 1], ele_seq[i][j]) in linear_order:
                        linear_order.remove((ele_seq[i][j + 1], ele_seq[i][j]))

            # hasse diagram
            hasse = nx.DiGraph()
            hasse.add_nodes_from(ele_seq[0])
            hasse.add_edges_from(linear_order)
            self.prune_subgraph(hasse)
            try:
                w = max([len(o) for o in nx.antichains(hasse)])
            except nx.exception.NetworkXUnfeasible:
                print(hasse.edges)
            h = nx.dag_longest_path_length(hasse)
            # h = len([e for e in hasse.nodes if pruned_subgraph.nodes[element2edge[e][0]]['label'] != '1'])
            hasse_graphs[index] = [(w, h), {edge for edge in hasse.edges()}, list(hasse.nodes), hasse]

        return element_sequences, element_seq_to_path_map, sorted(hasse_graphs.values(), key=lambda x: (x[0][0], -x[0][1]), reverse=True)
    
    def get_all_decomp_nodes(self, buchi_graph):
        init_acpt = self.get_init_accept(buchi_graph)
        decomp_sets = set()
        edges_to_be_removed = []
        for pair, _ in init_acpt:
            init_state, accept_state = pair[0], pair[1]
            pruned_subgraph, paths, removed_edge = self.get_subgraph(init_state, accept_state, buchi_graph)
            edges_to_be_removed.extend(removed_edge)
            edge2element, _ = self.get_element(pruned_subgraph)
            if not edge2element:
                continue
            element_sequences, element_seq_to_path_map, _ = self.map_path_to_element_sequence(edge2element, paths)
            
            # [[[1, 2], [2, 1]], [[3]]]
            for sequences in element_sequences: 
                # [[1, 2], [2, 1]]
                for seq in sequences:
                    # [1, 2]
                    if len(seq) == 1:
                        break
                    for idx in range(len(seq)-1):
                        if seq[idx+1:] + seq[:idx+1] in sequences:
                            path = element_seq_to_path_map[tuple(seq)]
                            # print(f'idx {idx}, node {path[idx+1]}')
                            decomp_sets.add(path[idx+1])

            # print('element_sequences')
            # print(element_sequences)
            # print('element2edge')
            # print(element2edge)
            # print('edge2element')
            # print(edge2element)
            # print('decomp_sets')
            # print(decomp_sets)
            # print('element_seq_to_path_map')
            # print(element_seq_to_path_map)
        for node in decomp_sets:
            buchi_graph.nodes[node]['color'] = 'red'
        buchi_graph.remove_edges_from(edges_to_be_removed)
        
        # remove node with zero indegree
        nodes_to_be_removed = []
        for node in buchi_graph.nodes():
            if 'init' not in node and buchi_graph.in_degree(node) == 0:
                nodes_to_be_removed.append(node)
        buchi_graph.remove_nodes_from(nodes_to_be_removed)
        buchi_graph.graph['init'] = tuple(buchi_graph.graph['init'])
        buchi_graph.graph['accept'] = tuple(buchi_graph.graph['accept'])
        return decomp_sets
    
    
    def get_ordered_subtasks(self, buchi_graph):
        init_acpt = self.get_init_accept(buchi_graph)
        for pair, _ in init_acpt:
            init_state, accept_state = pair[0], pair[1]
            pruned_subgraph, paths, _ = self.get_subgraph(init_state, accept_state, buchi_graph)
            edge2element, element2edge = self.get_element(pruned_subgraph)
            if not edge2element:
                continue
            _, _, hasse_graphs = self.map_path_to_element_sequence(edge2element, paths)
            return pruned_subgraph, hasse_graphs[0], element2edge
            
    @staticmethod
    def get_positive_literals(expr):
        positive_literals = set()
        
        # Helper function to handle individual clauses
        def handle_clause(clause):
            if clause.func is not Not:
                if clause.func is And:
                    for literal in clause.args:
                        if literal.func is not Not:
                            positive_literals.add(str(literal))
                else:
                    positive_literals.add(str(clause))
        
        if expr.func is Or:
            for clause in expr.args:
                handle_clause(clause)
        else:
            handle_clause(expr)
        
        return positive_literals
    
    @staticmethod
    def get_literals(expr):
        literals = set()
        
        # Helper function to handle individual clauses
        def handle_clause(clause):
            if clause.func is And:
                for literal in clause.args:
                    if literal.func is Not:
                        literals.add(str(literal.args[0]))
                    else:
                        literals.add(str(literal))
            else:
                if clause.func is Not:
                    literals.add(str(clause.args[0]))
                else:
                    literals.add(str(clause))
        
        if expr.func is Or:
            for clause in expr.args:
                handle_clause(clause)
        else:
            handle_clause(expr)
        
        return literals