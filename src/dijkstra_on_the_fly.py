import networkx as nx
from heapq import heappush, heappop
from itertools import count
from util import prCyan, prYellow
from data_structure import Node
from product_ts import ProductTs
from sympy import symbols

"""Modified from function multi_source_multi_targets_dijkstra in nx.algorithms
"""

def reach_target(v: Node):
    for q in v.phis_progress['p0']:
        if 'accept' in q:
            return True
    return False

def _dijkstra_multisource(
   sources, task_hierarchy, workspace, leaf_phis_order, depth_specs, paths=None, vis=False
):
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
    push = heappush
    pop = heappop
    dist = {}  # dictionary of final distances
    seen = {}
    # fringe is heapq with 3-tuples (distance,c,node)
    # use the count c to avoid comparing nodes (may not be able to)
    fringe = []
    for source in sources:
        seen[source] = 0
        push(fringe, (0, source))
    target = None
    while fringe:
        (d, v) = pop(fringe)
        if vis:
            prYellow(f'pop {d}, {v}')
        # put phis into v
        # print(d, v)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        if reach_target(v):
            target = v
            break
        succ = ProductTs.produce_succ(v, task_hierarchy, workspace, leaf_phis_order, depth_specs)
        for u, cost in succ:
            if vis:
                print(f'succ {u}')
            if cost is None:
                continue
            vu_dist = dist[v] + cost
            # skip if phi has been reached
            # if phi in phis:
            #     continue
            if u in dist:
                u_dist = dist[u]
                if vu_dist < u_dist:
                    raise ValueError("Contradictory paths found:", "negative weights?")
            elif u not in seen or vu_dist < seen[u]:
                seen[u] = vu_dist
                push(fringe, (vu_dist, u))
                if vis:
                    prCyan(f"push {vu_dist}, {u}")
                if paths is not None:
                    paths[u] = paths[v] + [u]
            # elif vu_dist == seen[u_phis]:
            #     if pred is not None:
            #         pred[u].append(v)

    # The optional predecessor and path dictionaries can be accessed
    # by the caller via the pred and paths objects passed as arguments.
    return dist, target

def multi_source_multi_targets_dijkstra(sources, task_hierarchy, workspace, leaf_spec_order, depth_specs):
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
        sources, task_hierarchy, workspace, leaf_spec_order, depth_specs, paths=paths, 
    )
    try: 
        return (dist[target], paths[target])
    except KeyError as err:
        raise nx.NetworkXNoPath(f"No path to {target}.") from err