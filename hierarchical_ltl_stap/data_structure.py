from collections import namedtuple

Hierarchy = namedtuple('Hierarchy', ['level', 'phi', 'buchi_graph', 'decomp_sets', 'hass_graph', 'element2edge'])
SpecInfo = namedtuple("SpecInfo", ['depth_specs', 'path_to_root', 'leaf_spec_order'])
PrimitiveSubtask = namedtuple('PrimitiveSubtask', ['element_in_poset'])
CompositeSubtask = namedtuple('CompositeSubtask', ['subtask2element'])
PrimitiveSubtaskId = namedtuple('PrimitiveSubtaskId', ['parent', 'element'])

class Node:
    def __init__(self, phi, type_robot, action, action_state, type_robots_x, phis_progress, world_state, progress_metric, obj_history):
        # rescue {(1, 0): (1, 0), (1, 1): (23, 0), (2, 0): (25, 1), (2, 1): (24, 1)} {'p0': 'T0_init', 'p200': 'T0_S2'} {'help', 'no_injury'}
        # action          robot state after taking action                      buchi state due to last action     world state after taking action
        # specific spec
        self.phi = phi
        # # specific type_robot 
        self.type_robot = type_robot
        # snapshot of type_robots distribution: dict[type_robot] = x
        self.type_robots_x = type_robots_x
        self.action = action
        # state in action model
        self.action_state = action_state
        # progress of all specs: dict[spec] = q
        self.phis_progress = phis_progress
        # snapshot of world state set()
        self.world_state = world_state
        self.progress_metric = progress_metric
        # history of manipulating objects
        self.obj_history = obj_history
        
    # Implementing __eq__ is necessary to compare objects for equality
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.phi == other.phi and self.type_robot == other.type_robot and \
                self.hash_dict(self.type_robots_x) == self.hash_dict(other.type_robots_x) and \
                    self.hash_dict(self.phis_progress) == self.hash_dict(other.phis_progress)
        return False
    
    def __lt__(self, other):
        if isinstance(other, Node):
            num_self_accept = len([q for q in self.phis_progress.values() if 'accept' in q ])
            num_other_accept = len([q for q in other.phis_progress.values() if 'accept' in q ])
            return num_self_accept < num_other_accept
        return NotImplemented
    
    # Implementing __hash__ method to make instances usable as keys in dictionaries
    def __hash__(self):
        return hash((self.phi, self.type_robot, self.hash_dict(self.type_robots_x), 
                     self.hash_dict(self.phis_progress), self.hash_set(self.world_state)))
    
    def hash_dict(self, d):
        return hash(tuple(sorted(d.items())))
    
    def hash_set(self, d):
        return hash(tuple(d))
    
    def __str__(self):
        return f"{self.phi} {self.type_robot} ({self.action}, {self.action_state}) {self.type_robots_x} {self.phis_progress} {self.world_state}"
