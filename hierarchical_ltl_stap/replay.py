"""Portable records of planner results, including the hierarchy and action trace."""
import json
from pathlib import Path
import subprocess

SCENARIOS = {12: 1, 13: 2, 14: 3, 21: 4}


def robot_id(robot):
    return f'{robot[0]}:{robot[1]}'


def export_replay(filename, args, workspace, specs, hierarchy_graph, task_hierarchy,
                  optimal_path, robot_path, robot_phi, robot_act, cost, seconds):
    formulas = {phi: formula for level in specs.hierarchy for phi, formula in level.items()}
    automata = {}
    for phi, hierarchy in task_hierarchy.items():
        graph = hierarchy.buchi_graph
        automata[phi] = {
            'initial': sorted(graph.graph['init']), 'accepting': sorted(graph.graph['accept']),
            'nodes': {q: str(data['label']) for q, data in graph.nodes(data=True)},
            'edges': [[u, v, str(data['label'])] for u, v, data in graph.edges(data=True)],
        }
    trace = [{
        'phi': node.phi, 'robot': robot_id(node.type_robot),
        'action': node.action, 'action_state': node.action_state,
        'positions': {robot_id(r): list(x) for r, x in node.type_robots_x.items()},
        'progress': node.phis_progress, 'world': sorted(node.world_state),
    } for node in optimal_path]
    data = {
        'version': 1, 'scenario': SCENARIOS.get(args.case), 'case': args.case,
        'provenance': {'source': 'actual planner execution', 'seed': args.seed,
                       'execution': 'simultaneous planner output; recorded stationary actions retained',
                       'collision_avoidance': False,
                       'cost_mode': args.cost, 'search_cost': cost, 'planning_seconds': seconds,
                       'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                       'heuristics': args.heuristics, 'heuristic_weight': args.heuristic_weight},
        'workspace': {'width': workspace.width, 'height': workspace.height,
                      'regions': workspace.regions, 'obstacles': workspace.obstacles,
                      'edges': list(workspace.graph_workspace.edges())},
        'domain': workspace.domain,
        'hierarchy': {'levels': specs.hierarchy, 'formulas': formulas,
                      'edges': list(hierarchy_graph.edges()), 'automata': automata},
        'robots': [{'id': robot_id(r), 'type': r[0], 'number': r[1],
                    'path': robot_path[r], 'actions': robot_act[r], 'tasks': robot_phi[r]}
                   for r in sorted(robot_path)],
        'search_trace': trace,
    }
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')
    print(f'Saved planner replay: {path}')
