import networkx as nx
from heapq import heappush, heappop
from itertools import count
from .util import prCyan, prYellow
from .data_structure import Node, SpecInfo
from .product_ts import ProductTs
from sympy import symbols

import sys
"""Modified from function multi_source_multi_targets_dijkstra in nx.algorithms
"""

def generate_simultaneous_horizon(optimal_path, workspace, leaf_spec_order):
    # Divide the optimal path into several segments corresponding to the phis
    # such that each segment only contains active robots that fulfill the phi.
    # it is possible that the path for a phi is interrupted 
    non_essential_actions = ['default', 'in-spec', 'inter-spec-i', 'inter-spec-ii']
    robot_path_act_per_phi = [] 
    temp_robot_path_act = dict()
    pre_phi = ''
    for wpt_act in optimal_path:
        if pre_phi and wpt_act.phi != pre_phi:
            robot_path_act_per_phi.append((pre_phi, temp_robot_path_act.copy()))
            temp_robot_path_act.clear()
        
        pre_phi = wpt_act.phi
        type_robot = wpt_act.type_robot
        x_act = (wpt_act.type_robots_x[type_robot], wpt_act.action)
        # remove identical x
        if type_robot in temp_robot_path_act.keys() and \
                (x_act[0] != temp_robot_path_act[type_robot][-1][0] or x_act[1] not in non_essential_actions):
            temp_robot_path_act[type_robot].append(x_act)
        elif type_robot not in temp_robot_path_act.keys():
            temp_robot_path_act[type_robot] = [x_act]
        
    robot_path_act_per_phi.append((pre_phi, temp_robot_path_act.copy()))
        
    ordered_phis = [phi for phi, _ in robot_path_act_per_phi] # phi in ordered_phis are at least as important as those phis that are behind it
    robot_path_len = {type_robot: 1 for type_robot in workspace.type_robot_location.keys()}
    phi_horizon = [0] * len(ordered_phis) # the latest time step when the specific phi is involved 
    for idx in range(len(ordered_phis)):
        curr_phi = ordered_phis[idx]
        # first phi
        # no need to consider other stuff, just parallel the path 
        if idx == 0:            
            for robot, path in robot_path_act_per_phi[idx][1].items():
                robot_path_len[robot] += len(path)
                phi_horizon[idx] = max(phi_horizon[idx], robot_path_len[robot])
            continue
            
        # (1) For each robot, find the phi that is the closest one behind (including) the current robot path
        # (2) Then between this phi and the final phi, determine the phi such that the robot must take action behind it
        # (3) Finally, add the robot path behind the time stamp determined by the phi
        for robot, path in robot_path_act_per_phi[idx][1].items():
            specific_robot_horizon = robot_path_len[robot]
            aligned_phi_idex = -1
            # find the phi within whose range the specific robot horizon lies
            if specific_robot_horizon >= phi_horizon[idx - 1]:
                aligned_phi_idex = idx - 1
            else:
                for pre_phi_idx in range(idx - 1, 0, -1):
                    if specific_robot_horizon < phi_horizon[pre_phi_idx] and \
                        specific_robot_horizon >= phi_horizon[pre_phi_idx - 1]:
                            aligned_phi_idex = pre_phi_idx
            if aligned_phi_idex == -1:
                aligned_phi_idex = 0
                
            horizon_of_closest_pred_phi = -1
            for pre_phi_idx in range(idx-1, aligned_phi_idex - 1, -1): 
                pre_phi = ordered_phis[pre_phi_idx]
                pre_phi_prior_to_current_phi = curr_phi in leaf_spec_order[pre_phi]
                current_phi_to_prior_pre_phi = pre_phi in leaf_spec_order[curr_phi]
                is_independent = pre_phi_prior_to_current_phi and current_phi_to_prior_pre_phi
                if not is_independent or ordered_phis[pre_phi_idx] == curr_phi:
                    horizon_of_closest_pred_phi = max(phi_horizon[pre_phi_idx], horizon_of_closest_pred_phi)
            # align
            robot_path_len[robot] += max(0, horizon_of_closest_pred_phi - robot_path_len[robot])
            # concatenate
            robot_path_len[robot] += len(path)
            phi_horizon[idx] = max(phi_horizon[idx], robot_path_len[robot])
   
    robot_act_len = {type_robot: 0 for type_robot in workspace.type_robot_location.keys()}
    for wpt_act in optimal_path:
        type_robot = wpt_act.type_robot
        robot_act_len[type_robot] += 0 if wpt_act.action in non_essential_actions else 1
    for i, wpt_act in enumerate(optimal_path):
        if i > 1:
            type_robot = wpt_act.type_robot
            robot_act_len[type_robot] += 0 if wpt_act.type_robots_x[type_robot] == optimal_path[i-1].type_robots_x[type_robot] else 0.1
    return tuple([robot_path_len[type_robot] + robot_act_len[type_robot] for type_robot in robot_path_len.keys()])
        
def update_cost(path: list, cost_to_come: float | tuple, step_cost: float, workspace, leaf_spec_order, args):
    if args.cost == 'minmax':
        assert isinstance(cost_to_come, tuple)
        updated_cost = generate_simultaneous_horizon(path, workspace, leaf_spec_order)
        return updated_cost
    elif args.cost == "min":
        assert isinstance(cost_to_come, float)
        return cost_to_come + step_cost
    else:
        assert False        

def calculate_cost(cost_to_come: float | tuple, args):
    if args.cost == 'minmax':
        assert isinstance(cost_to_come, tuple)
        weight = 0.9
        return weight * max(cost_to_come) + (1 - weight) * sum(cost_to_come)
    elif args.cost == 'min':
        assert isinstance(cost_to_come, float)
        return cost_to_come
    else:
        assert False
         
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
        # total_d: total cost combining nav distance and task progress
        # state_d: nav distance
        total_d = 0.0
        state_d = 0.0 if args.cost == 'min' else tuple([0.0]*len(source.type_robots_x.keys()))
        seen[source] = (total_d, state_d)
        push(fringe, (total_d, state_d, source))
    target = None
    expand_count = 0
    use_heuristics = args.heuristics or args.heuristics_automaton
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
            vu_state_dist = update_cost(paths[v] + [u], dist[v][1], cost, workspace, spec_info.leaf_spec_order, args)
            vu_total_dist = calculate_cost(vu_state_dist, args) - args.heuristic_weight * u.progress_metric * int(use_heuristics)
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
        return (calculate_cost(dist[target][1], args), paths[target])
    except KeyError as err:
        raise nx.NetworkXNoPath(f"No path to {target}.") from err