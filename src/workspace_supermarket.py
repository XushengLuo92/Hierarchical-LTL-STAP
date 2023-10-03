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
        self.type_num = {1: 2, 2: 2}   # single-task robot
        self.num_of_regions = 8
        self.num_of_obstacles = 6
        self.occupied = []
        self.n_shelf = 6
        self.regions = {'p{0}'.format(i): j for i, j in enumerate(self.allocate_region_dars())}
        self.obstacles = {'o{0}'.format(i+1): j for i, j in enumerate(self.allocate_obstacle_dars())}
        self.length = max([cell[1]+1 for region in self.regions.values() for cell in region]) # 9   # length
        self.width = max([cell[0]+1 for region in self.regions.values() for cell in region]) # 9   # width
        self.type_robot_location = self.initialize()
        # print(self.type_robot_location.keys())
        # self.type_robot_location[(1, 0)] = (0, 0)
        # self.type_robot_location[(1, 1)] = (24, 0)
        # self.type_robot_location[(2, 0)] = (1, 0)
        # self.type_robot_location[(2, 1)] = (25, 0)
        # customized location
        # self.type_robot_location[(2, 0)]  = (0, 0) # nav task 4
        # [region and corresponding locations
        self.label_location = {'r{0}'.format(i + 1): j for i, j in enumerate(list(self.type_robot_location.values()))}
        # [region where robots reside
        self.type_robot_label = dict(zip(self.type_robot_location.keys(), self.label_location.keys()))

        self.graph_workspace = nx.Graph()
        self.build_graph()
        self.domain = self.get_domain(domain_file)

        # self.p2p = self.point_to_point_path()  # label2label path

    def reachable(self, location, obstacles):
        next_location = [(location, location)]
        # left
        if location[0]-1 > 0 and (location[0]-1, location[1]) not in obstacles:
            next_location.append((location, (location[0]-1, location[1])))
        # right
        if location[0]+1 < self.width and (location[0]+1, location[1]) not in obstacles:
            next_location.append((location, (location[0]+1, location[1])))
        # up
        if location[1]+1 < self.length and (location[0], location[1]+1) not in obstacles:
            next_location.append((location, (location[0], location[1]+1)))
        # down
        if location[1]-1 > 0 and (location[0], location[1]-1) not in obstacles:
            next_location.append((location, (location[0], location[1]-1)))
        return next_location

    def build_graph(self):
        obstacles = list(itertools.chain(*self.obstacles.values()))
        for i in range(self.width):
            for j in range(self.length):
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

    def point_to_point_path(self):
        key_region = list(self.regions.keys())
        key_init = list(self.label_location.keys())

        p2p = dict()
        for l1 in range(len(self.regions)):
            for l2 in range(l1, len(self.regions)):
                min_length = np.inf
                for source in self.regions[key_region[l1]]:
                    for target in self.regions[key_region[l2]]:
                        length, _ = nx.algorithms.single_source_dijkstra(self.graph_workspace, source=source,
                                                                         target=target)
                        if length < min_length:
                            min_length = length
                p2p[(key_region[l1], key_region[l2])] = min_length
                p2p[(key_region[l2], key_region[l1])] = min_length
        # with open('data/p2p_large_workspace', 'wb') as filehandle:
        #     pickle.dump(p2p, filehandle)
        # with open('data/p2p_large_workspace', 'rb') as filehandle:
        #     p2p = pickle.load(filehandle)
        for r1 in range(len(self.label_location)):
            for l1 in range(len(self.regions)):
                min_length = np.inf
                for target in self.regions[key_region[l1]]:
                    length, _ = nx.algorithms.single_source_dijkstra(self.graph_workspace,
                                                                    source=self.label_location[key_init[r1]],
                                                                    target=target)
                    if length < min_length:
                        min_length = length
                p2p[(key_init[r1], key_region[l1])] = min_length
                p2p[(key_region[l1], key_init[r1])] = min_length

        for r1 in range(len(self.label_location)):
            for r2 in range(r1, len(self.label_location)):
                length, path = nx.algorithms.single_source_dijkstra(self.graph_workspace,
                                                                    source=self.label_location[key_init[r1]],
                                                                    target=self.label_location[key_init[r2]])
                p2p[(key_init[r1], key_init[r2])] = length
                p2p[(key_init[r2], key_init[r1])] = length

        return p2p
    
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

    def allocate_region_dars(self):
        regions = []        
        # ICRA
        shelf_width_x = 1
        shelf_length_y = 1
        start_dock_x = 0
        dock_width_x = 2
        dock_length_y = 1
        first_shelf_to_dock_x = 0
        first_shelf_to_dock_y = 1
        inter_shelf_x = 3
        depot_to_last_shelf_x = 1
        depot_width_x = 2
        depot_length_y = 2
        
        # p0 dock
        # p1 grocery p2 health p3 outdors p4 pet p5 furniture p6 electronics 
        # p7 packing area
        regions.append(list(itertools.product(range(start_dock_x, start_dock_x + dock_width_x), range(0, dock_length_y)))) 
        for i in range(self.n_shelf):
            regions.append(list(itertools.product([dock_width_x + first_shelf_to_dock_x + 
                                                    i * (shelf_width_x + inter_shelf_x) - 1,
                                                    dock_width_x + first_shelf_to_dock_x + 
                                                    i * (shelf_width_x + inter_shelf_x) + shelf_width_x], 
                                                range(dock_length_y + first_shelf_to_dock_y,
                                                    dock_length_y + first_shelf_to_dock_y + shelf_length_y))))
            
            
        regions[0].extend(list(itertools.product(range(dock_width_x + first_shelf_to_dock_x + 
                                                    (self.n_shelf - 1) * (shelf_width_x + inter_shelf_x) + shelf_width_x + depot_to_last_shelf_x,
                                                        dock_width_x + first_shelf_to_dock_x +
                                                    (self.n_shelf - 1) * (shelf_width_x + inter_shelf_x) + shelf_width_x + depot_to_last_shelf_x + depot_width_x),
                                            range(0, depot_length_y))))
        return regions

    def allocate_obstacle_dars(self):
        obstacles = []
        # ICRA
        shelf_width_x = 1
        shelf_length_y = 1
        dock_width_x = 2
        dock_length_y = 1
        first_shelf_to_dock_x = 0
        first_shelf_to_dock_y = 1
        inter_shelf_x = 3
        
        # p0 charging station
        # p1 grocery p2 health p3 outdors p4 pet p5 furniture p6 electronics
        for i in range(self.n_shelf):
            obstacles.append(list(itertools.product(range(dock_width_x + first_shelf_to_dock_x + 
                                                        i * (shelf_width_x + inter_shelf_x),
                                                        dock_width_x + first_shelf_to_dock_x + 
                                                        i * (shelf_width_x + inter_shelf_x) + shelf_width_x), 
                                                  range(dock_length_y + first_shelf_to_dock_y,
                                                        dock_length_y + first_shelf_to_dock_y + shelf_length_y))))
            

        return obstacles

    def initialize(self):
        type_robot_location = dict()
        x0 = copy.deepcopy(self.regions['p0'])
        # random.seed(1)
        for robot_type in self.type_num.keys():
            for num in range(self.type_num[robot_type]):
                while True:
                    candidate = random.sample(x0, 1)[0]
                    if candidate not in type_robot_location.values():
                        type_robot_location[(robot_type, num)] = candidate
                        x0.remove(candidate)
                        break
        return type_robot_location
    
    def get_domain(self, domain_file):
        with open(domain_file, 'r') as f:
            return json.load(f)
        
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
            
    def get_obsevation_based_actions(self, robot_type, aps):
        """get actions based on observations

        Args:
            aps (_type_): _description_

        Returns:
            _type_: _description_
        """
        actions = []
        for action, preconds_effs in self.domain.get('robot_actions').items():
            for preconds in preconds_effs['preconditions']:
                if all(element in aps for element in preconds if "!" not in element) and \
                    all(element[1:] not in aps for element in preconds if "!" in element):
                    actions.append(action)
        if not actions:
            actions.append('navigate')
        
        return [action for action in actions if action == 'navigate' or action in self.domain.get('robot_group')[str(robot_type)]]
    
    def update_world_state(self, robot_state, robot_action, world_state):
        """update world state base on action

        Args:
            world_state (_type_): _description_
            action (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        new_world_state = world_state.copy()
        # update based on environment action
        robot_state_observ = []
        for region, cells in self.regions.items():
            if robot_state in cells:
                robot_state_observ = [region]
                break
        for env_action, preconds_effs in self.domain.get('env_actions').items():
            for preconds in preconds_effs['preconditions']:
                if all(element in robot_state_observ for element in preconds if "!" not in element) and \
                    all(element[1:] not in world_state for element in preconds if "!" in element):
                    new_world_state.add(env_action)
        # update based on robot action            
        if robot_action == 'navigate':
            return new_world_state
        for effect in self.domain.get("robot_actions")[robot_action]["effects"]:
            if "!" not in effect:
                new_world_state.add(effect)
            else:
                new_world_state.discard(effect[1:])

        return new_world_state
    
    def update_robot_state(self, robot_state):
        """update robot loc state in navigate action

        Args:
            robot_state (_type_): _description_

        Returns:
            _type_: _description_
        """
        return list(self.graph_workspace.neighbors(robot_state))