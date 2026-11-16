"""Finite-trace LTL checks for the exported execution and its task hierarchy.

Leaf formulas are evaluated on each assigned robot's task-labelled action trace.
Parent formulas consume persistent child-completion propositions. The first four
README scenarios use conjunctions of eventual child completions.
"""
from functools import lru_cache
from itertools import combinations
import re

class FormulaParser:
    def __init__(self, formula):
        token = r'\[\]|<>|&&|\|\||->|[!()]|[A-Za-z][A-Za-z0-9_]*'
        self.tokens = re.findall(token, formula)
        if ''.join(self.tokens) != re.sub(r'\s+', '', formula):
            raise ValueError('Unsupported LTL token.')
        self.index = 0

    def peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self):
        value = self.peek()
        self.index += 1
        return value

    def parse(self):
        node = self.expression(0)
        if self.peek() is not None:
            raise ValueError(f'Unexpected token {self.peek()}')
        return node

    def expression(self, minimum):
        value = self.take()
        if value in ('!', '[]', '<>', 'X'):
            left = (value, self.expression(5))
        elif value == '(':
            left = self.expression(0)
            if self.take() != ')':
                raise ValueError('Missing closing parenthesis.')
        elif value is not None and re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]*', value) and value != 'U':
            left = ('atom', value)
        else:
            raise ValueError(f'Unexpected token {value}')
        # Match ltl2ba/parse.c: Boolean binary operators share a level,
        # until binds more tightly, and both levels associate to the left.
        priorities = {'->': 1, '||': 1, '&&': 1, 'U': 2}
        while self.peek() in priorities and priorities[self.peek()] >= minimum:
            operator = self.take()
            priority = priorities[operator]
            right = self.expression(priority + 1)
            left = (operator, left, right)
        return left


def finite_truth(formula, trace):
    """LTLf with strong next/until; no artificial loop or padded final state."""
    if not trace:
        return False
    tree = FormulaParser(formula).parse() if isinstance(formula, str) else formula

    @lru_cache(None)
    def evaluate(node):
        op = node[0]
        if op == 'atom':
            return tuple(node[1] == 'true' or node[1] in row for row in trace)
        a = evaluate(node[1])
        if op == '!':
            return tuple(not value for value in a)
        if op == 'X':
            return a[1:] + (False,)
        if op in ('<>', '[]', 'U'):
            b = evaluate(node[2]) if op == 'U' else None
            value = op == '[]'
            result = []
            for i in reversed(range(len(trace))):
                value = (a[i] and value) if op == '[]' else (a[i] or value) if op == '<>' else (b[i] or (a[i] and value))
                result.append(value)
            return tuple(reversed(result))
        b = evaluate(node[2])
        if op == '&&': return tuple(x and y for x, y in zip(a, b))
        if op == '||': return tuple(x or y for x, y in zip(a, b))
        if op == '->': return tuple(not x or y for x, y in zip(a, b))
        raise ValueError(op)
    return evaluate(tree)[0]


def observations(data, robot, step):
    point = robot['path'][step]
    obs = {key for key, cells in data['workspace']['regions'].items() if point in cells}
    obs.add(robot['actions'][step])
    return obs


class Monitor:
    def __init__(self, data):
        self.data = data
        self.horizon = max(len(r['path']) for r in data['robots']) - 1
        self.formulas = data['hierarchy']['formulas']
        self.children = {phi: [] for phi in self.formulas}
        for parent, child in data['hierarchy']['edges']:
            self.children[parent].append(child)
        self.leaves = [phi for phi in self.formulas if not self.children[phi]]
        self.completed = {}
        self.assigned = {phi: [] for phi in self.leaves}
        self.active_steps = {}
        self.leaf_results = {}
        self.witness_robot = {}
        for phi in self.leaves:
            tree = FormulaParser(self.formulas[phi]).parse()
            results = []
            active = []
            for robot in data['robots']:
                steps = [t for t, task in enumerate(robot['tasks']) if task == phi]
                if not steps:
                    continue
                self.assigned[phi].append(robot['id'])
                active.extend(steps)
                trace = [observations(data, robot, t) for t in steps]
                valid = finite_truth(tree, trace)
                results.append({'robot': robot['id'], 'satisfied': valid, 'steps': len(steps)})
                # Only retain a witness if the complete scoped trace passes,
                # so a later safety violation cannot be hidden by an early prefix.
                if valid:
                    for length in range(1, len(trace)+1):
                        if finite_truth(tree, trace[:length]):
                            time = steps[length-1]
                            if time < self.completed.get(phi, float('inf')):
                                self.completed[phi] = time
                                self.witness_robot[phi] = robot['id']
                            break
            self.active_steps[phi] = sorted(set(active))
            self.leaf_results[phi] = results
        for level in reversed(data['hierarchy']['levels']):
            for phi in level:
                if not self.children[phi]:
                    continue
                trace = [{child for child in self.children[phi] if self.completed.get(child, float('inf')) <= t}
                         for t in range(self.horizon+1)]
                if finite_truth(self.formulas[phi], trace):
                    for t in range(self.horizon+1):
                        if finite_truth(self.formulas[phi], trace[:t+1]):
                            self.completed[phi] = t
                            break

    def status(self, phi, step):
        if self.completed.get(phi, float('inf')) <= step:
            return 'done'
        if phi in self.leaves:
            return 'active' if int(step) in self.active_steps[phi] else 'pending'
        return 'active' if any(self.status(c, step) != 'pending' for c in self.children[phi]) else 'pending'

    def validate(self):
        movement_errors, action_errors, safety_errors, conflicts = [], [], [], []
        robots = self.data['robots']
        edges = {tuple(map(tuple, e)) for e in self.data['workspace']['edges']}
        vertices = {p for edge in edges for p in edge}
        model = self.data['domain']['action_model']
        for robot in robots:
            states = {'x'}
            for t, (point, action) in enumerate(zip(robot['path'], robot['actions'])):
                p = tuple(point)
                obs = observations(self.data, robot, t)
                if p not in vertices or (t and (tuple(robot['path'][t-1]), p) not in edges and (p, tuple(robot['path'][t-1])) not in edges):
                    movement_errors.append({'robot': robot['id'], 'step': t, 'cell': point})
                if t:
                    states = {edge['to'] for edge in model['edges'] if edge['from'] in states and edge['label'] == action}
                    if not states:
                        action_errors.append({'robot': robot['id'], 'step': t, 'action': action})
                preconditions = self.data['domain']['robot_actions'][action]['preconditions']
                before = observations(self.data, robot, max(t-1, 0))
                if not any(all((p[1:] not in before) if p.startswith('!') else p in before for p in clause) for clause in preconditions):
                    action_errors.append({'robot': robot['id'], 'step': t, 'reason': 'action precondition'})
                if action in ('carry', 'carrybin') and 'publicc' in obs:
                    safety_errors.append({'robot': robot['id'], 'step': t, 'reason': 'carrying in public'})
                if action in ('camera', 'photo') and not any(f'm{i}' in obs for i in range(1, 7)):
                    safety_errors.append({'robot': robot['id'], 'step': t, 'reason': 'camera outside meeting room'})
        for t in range(self.horizon+1):
            for a, b in combinations(robots, 2):
                if a['path'][t] == b['path'][t]:
                    conflicts.append({'step': t, 'robots': [a['id'], b['id']], 'kind': 'vertex'})
                elif t and a['path'][t] == b['path'][t-1] and b['path'][t] == a['path'][t-1]:
                    conflicts.append({'step': t, 'robots': [a['id'], b['id']], 'kind': 'edge swap'})
        final = self.data['search_trace'][-1]['progress']
        search_accepted = all(final[phi] in self.data['hierarchy']['automata'][phi]['accepting'] for phi in self.formulas)
        return {'scenario': self.data['scenario'], 'case': self.data['case'], 'robots': len(robots),
                'horizon': self.horizon, 'planner_accepted': search_accepted,
                'hierarchy_satisfied': 'p0' in self.completed, 'completion_steps': self.completed,
                'leaf_checks': self.leaf_results, 'legal_grid_paths': not movement_errors,
                'action_model_valid': not action_errors, 'safety_valid': not safety_errors,
                'movement_errors': movement_errors, 'action_errors': action_errors, 'safety_errors': safety_errors,
                'collision_free': not conflicts, 'conflicts': conflicts,
                'semantics': 'finite per-robot task-labelled leaf traces; parent formulas over child completion events',
                'collision_note': 'The upstream simultaneous execution scheduler does not enforce robot-robot collision avoidance.'}
