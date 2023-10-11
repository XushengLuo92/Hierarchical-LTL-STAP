# -*- coding: utf-8 -*-

from random import randint
import networkx as nx
import matplotlib.pyplot as plt

import numpy as np
import random
import sys
import itertools
import pickle
import copy
import json
import subprocess

class Workspace(object):
    """
    define the workspace where robots reside
    """
    def __init__(self, domain_file='./src/default_domain.json'):
        # dimension of the workspace
        # self.length = int(sys.argv[1])
        # self.width = int(sys.argv[1])
        # n = int(sys.argv[2])
        # n = 4
        self.type_num = {1: 6}  # single-task robot
        # self.num_of_regions = 8
        # self.num_of_obstacles = 6
        self.occupied = []
        self.n_shelf = 6
        self.regions = self.allocate_regions()
        self.obstacles = self.allocate_obstacles()
        self.height = 8
        self.width = 31
        robots_of_interest = {1, 2, 3, 4, 5, 6}
        # self.type_robot_location = {(1, r): self.regions['r'+str(r)][0] for r in robots_of_interest}
        self.type_robot_location = self.allocate_init_locs(robots_of_interest)
        # [region and corresponding locations
        self.label_location = {'r{0}'.format(r): self.type_robot_location[(1, r)] for r in robots_of_interest}
        # [region where robots reside
        self.type_robot_label = dict(zip(self.type_robot_location.keys(), self.label_location.keys()))

        self.graph_workspace = nx.Graph()
        self.build_graph()
        self.domain = self.get_domain(domain_file)
        self.load_action_model()

    def reachable(self, location, obstacles):
        next_location = [(location, location)]
        # left
        if location[0]-1 > 0 and (location[0]-1, location[1]) not in obstacles:
            next_location.append((location, (location[0]-1, location[1])))
        # right
        if location[0]+1 < self.width and (location[0]+1, location[1]) not in obstacles:
            next_location.append((location, (location[0]+1, location[1])))
        # up
        if location[1]+1 < self.height and (location[0], location[1]+1) not in obstacles:
            next_location.append((location, (location[0], location[1]+1)))
        # down
        if location[1]-1 > 0 and (location[0], location[1]-1) not in obstacles:
            next_location.append((location, (location[0], location[1]-1)))
        return next_location

    def build_graph(self):
        obstacles = list(itertools.chain(*self.obstacles.values()))
        for i in range(1, self.width):
            for j in range(1, self.height):
                if (i, j) not in obstacles:
                    self.graph_workspace.add_edges_from(self.reachable((i, j), obstacles))

    def get_atomic_prop(self):
        atomic_prop = dict()
        for type_robot, location in self.type_robot_location.items():
            for region, cells in self.regions.items():
                if location in cells:
                    if (region, type_robot[0]) not in atomic_prop.keys():
                        atomic_prop[(region, type_robot[0])] = 1
                    else:
                        atomic_prop[(region, type_robot[0])] += 1
        return atomic_prop

    def path_plot(self, robot_path):
        """
        plot the path
        :param path: found path
        :param workspace: workspace
        :param number_of_robots:
        :return: figure
        """

        for robot, path in robot_path.items():
            # prefix path
            if len(path) == 1:
                continue
            x_pre = np.asarray([point[0] + 0.5 for point in path])
            y_pre = np.asarray([point[1] + 0.5 for point in path])
            plt.quiver(x_pre[:-1], y_pre[:-1], x_pre[1:] - x_pre[:-1], y_pre[1:] - y_pre[:-1],
                       color="#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]),
                       scale_units='xy', angles='xy', scale=1, label='prefix path')

            plt.savefig('img/path.png', bbox_inches='tight', dpi=600)

    def allocate_regions(self):
        regions = {
            'd1': [(2, 7)],
            'd2': [(5, 7)],
            'd3': [(14, 7)],
            'd4': [(17, 7)],
            'd5': [(27, 7)],
            'd6': [(30, 7)],
            'd7': [(30, 2)],
            'd8': [(20, 1)],
            'd9': [(17, 1)],
            'd10': [(14, 1)],
            'd11': [(11, 1)],
            'd12': [(8, 1)],
            'd13': [(4, 1)],
            'd14': [(2, 1)],
            'm1': [(8, 7)],
            'm2': [(24, 7)],
            'm3': [(28, 5)],
            'm4': [(28, 3)],
            'm5': [(6, 1)],
            'm6': [(4, 5)],
            # 'r1': [(5, 7)],
            # 'r2': [(7, 6)],
            # 'r3': [(7, 2)],
            # 'r4': [(25, 2)],
            # 'r5': [(30, 7)],
            # 'r6': [(20, 1)],
            'publicc': [(21, 6), (22, 6), (23, 6)],
            'e': [(21, 7)],
            'p': [(17, 3)],
            'k': [(11, 3)],
            'g': [(11, 7)],
        }  
        
        return regions

    def allocate_obstacles(self):
        obstacles = {
            'obs': [(5, 1), (7, 1), (9, 1), (10, 1), (12, 1), (13, 1), (15, 1), (16, 1),
                    (18, 1), (19, 1)] + list(itertools.product(range(21, 31), [1]))
            + [(4, 7), (6, 7), (7, 7), (9, 7), (10, 7), (12, 7), (13, 7), (15, 7), (16, 7), 
               (18, 7), (19, 7), (20, 7), (22, 7), (23, 7), (25, 7), (26, 7), (28, 7), (29, 7)]
            + list(itertools.product(range(4, 8), range(3, 5))) + list(itertools.product(range(5, 8), [5]))
            + list(itertools.product(range(9, 11), [3])) + list(itertools.product(range(9, 12), range(4, 6)))
            + list(itertools.product(range(14, 17), [3])) + list(itertools.product(range(14, 18), range(4, 6)))
            + list(itertools.product(range(20, 25), range(3, 6)))
            + list(itertools.product([27], range(3, 6))) + [(28, 4)]
            + list(itertools.product([30], range(3, 6))) 
            + list(itertools.product([1], range(1, 8))) 
            + [(3, 1)]
        }
        
        return obstacles

    def allocate_init_locs(self, robots_of_interest):
        type_robot_location = dict()
        x_label = [x for region in self.regions.values() for x in region]
        x_label.extend([x for obs in self.obstacles.values() for x in obs])
        x_free = []
        for w in range(1, self.width):
            for h in range(1, self.height):
                if (w, h) not in x_label:
                    x_free.append((w, h))
        # random.seed(1)
        for robot_type in self.type_num.keys():
            for robot in robots_of_interest:
                while True:
                    candidate = random.sample(x_free, 1)[0]
                    if candidate not in type_robot_location.values():
                        type_robot_location[(robot_type, robot)] = candidate
                        x_free.remove(candidate)
                        break
        return type_robot_location
    
    def get_domain(self, domain_file):
        def remove_comments(json_str):
            return '\n'.join([line for line in json_str.split('\n') if not line.strip().startswith('//')])

        with open(domain_file, 'r') as f:
            data = f.read()

        cleaned_data = remove_comments(data)
        return json.loads(cleaned_data)
        
    def get_state_based_world_state(self, location, world_state):
        """generate observations

        Args:
            world_state (_type_): _description_
            location (_type_): _description_

        Returns:
            _type_: _description_
        """
        observations = world_state.copy()
        for region, cells in self.regions.items():
            if location in cells:
                observations.add(region)
                break
        for action, preconds_effs in self.domain.get('env_actions').items():
            for preconds in preconds_effs['preconditions']:
                if all(element in observations for element in preconds if "!" not in element) and \
                    all(element[1:] not in world_state for element in preconds if "!" in element):
                    observations.add(action)
        return observations
    
        
    def get_robot_state_based_observations(self, location):
        """generate observations, only involves location

        Args:
            world_state (_type_): _description_
            location (_type_): _description_

        Returns:
            _type_: _description_
        """
        observations = set()
        for region, cells in self.regions.items():
            if location in cells:
                observations.add(region)
                break
        return observations
            
    def get_obsevation_based_actions(self, robot_type, action_state, aps):
        """get actions based on observations

        Args:
            aps (_type_): _description_

        Returns:
            _type_: _description_
        """
        man_actions = []
        for succ in self.action_model.succ[action_state]:
            action = self.action_model.edges[(action_state, succ)]['label']
            for preconds in self.domain.get('robot_actions')[action]['preconditions']:
                if all(element in aps for element in preconds if "!" not in element) and \
                    all(element[1:] not in aps for element in preconds if "!" in element):
                    man_actions.append((action, succ))
                    break
        return [action for action in man_actions if action[0] in self.domain.get('robot_group')[str(robot_type)]]
    
    def update_world_state(self, robot_state, robot_action, world_state):
        """update world state base on action

        Args:
            world_state (_type_): _description_
            action (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        new_world_state = set(state for state in world_state if 'no_' in state)
        # update based on environment action
        robot_state_observ = []
        for region, cells in self.regions.items():
            if robot_state in cells:
                robot_state_observ = [region]
                break
        new_world_state.update(set(robot_state_observ))
        for env_action, preconds_effs in self.domain.get('env_actions').items():
            for preconds in preconds_effs['preconditions']:
                if all(element in robot_state_observ for element in preconds if "!" not in element) and \
                    all(element[1:] not in world_state for element in preconds if "!" in element):
                    new_world_state.add(env_action)
        # update based on robot action            
        for effect in self.domain.get("robot_actions")[robot_action]["effects"]:
            if "!" not in effect:
                new_world_state.add(effect)
            else:
                new_world_state.discard(effect[1:])

        return new_world_state
    
    def update_robot_state(self, robot_state):
        """update robot loc state in navigate mode

        Args:
            robot_state (_type_): _description_

        Returns:
            _type_: _description_
        """
        return list(self.graph_workspace.neighbors(robot_state))
    
    def load_action_model(self):
        # Create an empty directed graph
        self.action_model = nx.DiGraph()

        # Add nodes to the graph
        self.action_model.add_nodes_from(self.domain['action_model']['nodes'])

        # Add edges to the graph
        for edge in self.domain['action_model']['edges']:
            from_node = edge['from']
            to_node = edge['to']
            label = edge['label']
            self.action_model.add_edge(from_node, to_node, label=label)
        
        title = "./data/action_model"
        nx.nx_agraph.write_dot(self.action_model, title+'.dot')
        command = "dot -Tpng {0}.dot >{0}.png".format(title)
        subprocess.run(command, shell=True, capture_output=True, text=True)
        
    def name(self):
        return "bosch"