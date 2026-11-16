import copy
from types import SimpleNamespace
import unittest

from hierarchical_ltl_stap.demo_monitor import finite_truth, Monitor
from hierarchical_ltl_stap.execution import generate_simultaneous_exec


class FiniteLogicTests(unittest.TestCase):
    def test_next_requires_an_actual_next_observation(self):
        self.assertFalse(finite_truth('X default', [{'default'}]))
        self.assertTrue(finite_truth('X default', [set(), {'default'}]))

    def test_until_requires_discharge_but_allows_immediate_release(self):
        self.assertFalse(finite_truth('carry U dispose', [{'carry'}, {'carry'}]))
        self.assertTrue(finite_truth('carry U dispose', [{'dispose'}]))
        self.assertFalse(finite_truth('carry U dispose', [{'carry'}, set(), {'dispose'}]))

    def test_public_area_violation_is_not_forgotten(self):
        formula = '<> dispose && [](carry -> !publicc)'
        self.assertTrue(finite_truth(formula, [{'carry'}, {'dispose'}]))
        self.assertFalse(finite_truth(formula, [{'carry', 'publicc'}, {'dispose'}]))

    def test_drop_off_requires_next_step_without_carry(self):
        formula = '<> (p && carry U (d10 && X !carry))'
        self.assertFalse(finite_truth(formula, [{'p', 'carry'}, {'d10', 'carry'}]))
        self.assertTrue(finite_truth(formula, [{'p', 'carry'}, {'d10', 'carry'}, {'default'}]))

    def test_parser_matches_ltl2ba_until_precedence(self):
        self.assertTrue(finite_truth('p && carry U d10', [{'p', 'carry'}, {'carry'}, {'d10'}]))


class ExecutionTests(unittest.TestCase):
    def test_stationary_default_witness_survives_export(self):
        robot = (1, 1)
        workspace = SimpleNamespace(type_robot_location={robot: (2, 2)})
        path = [SimpleNamespace(phi='p1', type_robot=robot, type_robots_x={robot: (2, 2)}, action=a)
                for a in ('in-spec', 'emptybin', 'default', 'default')]
        positions, tasks, actions = generate_simultaneous_exec(path, workspace, {'p1': set()}, SimpleNamespace(print_path=False))
        self.assertEqual(actions[robot], ['default', 'emptybin', 'default', 'default'])
        self.assertEqual(tasks[robot], ['', 'p1', 'p1', 'p1'])
        self.assertEqual(len(positions[robot]), 4)



class HierarchyTests(unittest.TestCase):
    def data(self, actions):
        return {'workspace': {'regions': {}},
                'hierarchy': {'formulas': {'p0': '<> p1', 'p1': '<> done && [] !bad'},
                              'edges': [['p0', 'p1']], 'levels': [{'p0': '<> p1'}, {'p1': '<> done && [] !bad'}]},
                'robots': [{'id': '1:1', 'path': [[2, 2]]*len(actions), 'actions': actions, 'tasks': ['p1']*len(actions)}]}

    def test_parent_completion_and_backward_seeking(self):
        monitor = Monitor(self.data(['default', 'done']))
        self.assertEqual(monitor.status('p0', 1), 'done')
        self.assertNotEqual(monitor.status('p0', 0), 'done')
        self.assertEqual(monitor.completed['p1'], 1)

    def test_later_guard_violation_invalidates_completion(self):
        monitor = Monitor(self.data(['default', 'done', 'bad']))
        self.assertNotIn('p1', monitor.completed)
        self.assertNotIn('p0', monitor.completed)

    def test_collisions_are_diagnostics_and_do_not_change_execution(self):
        data = self.data(['default', 'done'])
        other = copy.deepcopy(data['robots'][0]); other['id'] = '1:2'
        data['robots'].append(other)
        data.update({'scenario': 1, 'case': 12,
                     'domain': {'action_model': {'edges': [
                         {'from': 'x', 'to': 'x', 'label': action} for action in ('default', 'done')]},
                                'robot_actions': {a: {'preconditions': [[]]} for a in ('default', 'done')}},
                     'search_trace': [{'progress': {'p0': 'accept', 'p1': 'accept'}}]})
        data['hierarchy']['automata'] = {p: {'accepting': ['accept']} for p in ('p0', 'p1')}
        data['workspace']['edges'] = [[[2, 2], [2, 2]]]
        original = copy.deepcopy(data)
        result = Monitor(data).validate()
        self.assertTrue(result['hierarchy_satisfied'])
        self.assertTrue(result['action_model_valid'])
        self.assertFalse(result['collision_free'])
        self.assertEqual(len(result['conflicts']), 2)
        self.assertEqual(data, original)


if __name__ == '__main__':
    unittest.main()
