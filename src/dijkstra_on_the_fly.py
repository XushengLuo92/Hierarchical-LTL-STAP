import networkx as nx
from heapq import heappush, heappop
from itertools import count
from util import prCyan, prYellow
from data_structure import Node, SpecInfo
from product_ts import ProductTs
from sympy import symbols

import sys
"""Modified from function multi_source_multi_targets_dijkstra in nx.algorithms
"""

def reach_target(v: Node):
    if 'accept' in v.phis_progress['p0']:
        return True
    return False

def at_most_one_non_decomp_states(phis_progress, leaf_specs, task_hierarchy):
    count_not_decomp_state = 0
    for spec in leaf_specs:
        q = phis_progress[spec]
        hierarchy = task_hierarchy[spec]
        decomp_set = hierarchy.decomp_sets | set(hierarchy.buchi_graph.graph['init']) | set(hierarchy.buchi_graph.graph['accept'])
        if q not in decomp_set:
            count_not_decomp_state += 1
        if count_not_decomp_state > 1:
            return False
    return True 

    

def _dijkstra_multisource(
   sources, task_hierarchy, workspace, spec_info, args, paths=None):
    """Uses Dijkstra's algorithm to find shortest weighted paths

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty iterable of nodes
        Starting nodes for paths. If this is just an iterable containing
        a single node, then all paths computed by this function will
        start from that node. If there are two or more nodes in this
        iterable, the computed paths may begin from any one of the start
        nodes.

    weight: function
        Function with (u, v, data) input that returns that edge's weight
        or None to indicate a hidden edge

    pred: dict of lists, optional(default=None)
        dict to store a list of predecessors keyed by that node
        If None, predecessors are not stored.

    paths: dict, optional (default=None)
        dict to store the path list from source to each node, keyed by node.
        If None, paths are not stored.

    target : node label, optional
        Ending node for path. Search is halted when target is found.

    cutoff : integer or float, optional
        Length (sum of edge weights) at which the search is stopped.
        If cutoff is provided, only return paths with summed weight <= cutoff.

    Returns
    -------
    distance : dictionary
        A mapping from node to shortest distance to that node from one
        of the source nodes.

    Raises
    ------
    NodeNotFound
        If any of `sources` is not in `G`.

    Notes
    -----
    The optional predecessor and path dictionaries can be accessed by
    the caller through the original pred and paths objects passed
    as arguments. No need to explicitly return pred or paths.

    """
    if args.log:
        with open('log.txt', 'w') as f:
            f.write('')
        original_stdout = sys.stdout
    
    push = heappush
    pop = heappop
    dist = {}  # dictionary of final distances
    seen = {}
    # fringe is heapq with 3-tuples (distance,c,node)
    # use the count c to avoid comparing nodes (may not be able to)
    fringe = []
    for source in sources:
        seen[source] = (0, 0)
        push(fringe, (0, 0, source))
    target = None
    expand_count = 0
    while fringe:
        expand_count += 1
        (total_d, state_d, v) = pop(fringe)
        if args.print_search:
            prYellow(f'pop ({total_d}, {state_d}), {v}')
        if args.log:
            with open('log.txt', 'a') as f:
                sys.stdout = f
                print("----------------------------------------")
                print(f'pop ({total_d}, {state_d}), {v}')
        # put phis into v
        # print(d, v)
        if v in dist:
            continue  # already searched this node.
        dist[v] = (total_d, state_d)
        if reach_target(v):
            target = v
            break
        succ = ProductTs.produce_succ(v, task_hierarchy, workspace, spec_info, args)
        for u, cost in succ:
            if not at_most_one_non_decomp_states(u.phis_progress, spec_info.leaf_spec_order.keys(), task_hierarchy):
                raise AssertionError("More than one automaton states are not decompoistion states.")

            if args.print_search:
                print(f'succ {u}')
            # print(f'succ {u}')

            if args.log:
                with open('log.txt', 'a') as f:
                    sys.stdout = f
                    print(f'succ {u}')
            if cost is None:
                continue
            vu_state_dist = dist[v][1] + cost
            vu_total_dist = vu_state_dist - args.heuristic_weight * u.progress_metric * int(args.heuristics)
            # skip if phi has been reached
            # if phi in phis:
            #     continue
            # if u in dist:
            #     u_dist = dist[u][0]
            #     if vu_dist < u_dist:
            #         raise ValueError("Contradictory paths found:", "negative weights?")
            if u not in seen or vu_total_dist < seen[u][0]:
                seen[u] = (vu_total_dist, vu_state_dist)
                push(fringe, (vu_total_dist, vu_state_dist, u))
                if args.print_search:
                    prCyan(f"push ({vu_total_dist}, {vu_state_dist}), {u}")
                if args.log:
                    with open('log.txt', 'a') as f:
                        sys.stdout = f
                        print(f"push ({vu_total_dist}, {vu_state_dist}), {u}")
                if paths is not None:
                    paths[u] = paths[v] + [u]
    if args.log:
        sys.stdout = original_stdout
    if args.print_search:
        prYellow(f"Expand node count {expand_count}")
    # The optional predecessor and path dictionaries can be accessed
    # by the caller via the pred and paths objects passed as arguments.
    return dist, target

def multi_source_multi_targets_dijkstra(sources, task_hierarchy, workspace, spec_info, args):
    """Find shortest weighted paths and lengths from a given set of
    source nodes.

    Uses Dijkstra's algorithm to compute the shortest paths and lengths
    between one of the source nodes and the given `target`, or all other
    reachable nodes if not specified, for a weighted graph.
    """
    if not sources:
        raise ValueError("sources must not be empty")
    paths = {source: [source] for source in sources}  # dictionary of paths
    dist, target = _dijkstra_multisource(
        sources, task_hierarchy, workspace, spec_info, args, paths=paths,
    )
    try: 
        return (dist[target][1], paths[target])
    except KeyError as err:
        raise nx.NetworkXNoPath(f"No path to {target}.") from err