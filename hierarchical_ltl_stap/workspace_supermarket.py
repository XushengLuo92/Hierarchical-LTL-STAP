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
    def __init__(self, domain_file='./src/default_domain.json', num_of_robots=6):
        # dimension of the workspace
        self.length = 15 # 9   # length
        self.width = 40 # 9   # width
        # n = int(sys.argv[2])
        # n = 4
        self.type_num = {1: num_of_robots}  # single-task robot
        self.num_of_regions = 8
        self.num_of_obstacles = 6
        self.occupied = []
        self.n_shelf = 6
        self.regions = {'p{0}'.format(i): j for i, j in enumerate(self.allocate_region_dars())}
        self.obstacles = {'o{0}'.format(i+1): j for i, j in enumerate(self.allocate_obstacle_dars())}
        self.height = max([cell[1]+1 for region in self.regions.values() for cell in region]) # 9   # length
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
        self.load_action_model()
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
        if location[1]+1 < self.height and (location[0], location[1]+1) not in obstacles:
            next_location.append((location, (location[0], location[1]+1)))
        # down
        if location[1]-1 > 0 and (location[0], location[1]-1) not in obstacles:
            next_location.append((location, (location[0], location[1]-1)))
        return next_location

    def build_graph(self):
        obstacles = list(itertools.chain(*self.obstacles.values()))
        for i in range(self.width):
            for j in range(self.height):
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
        shelf_width_x = 2
        shelf_length_y = 5
        start_charging_station_x = 2
        charging_station_width_x = 4
        charging_station_length_y = 6
        first_shelf_to_charging_station_x = 2
        first_shelf_to_charging_station_y = 2
        inter_shelf_x = 3
        depot_to_last_shelf_x = 2
        depot_width_x = 4
        depot_length_y = 4
        
        # p0 dock
        # p1 grocery p2 health p3 outdors p4 pet p5 furniture p6 electronics 
        # p7 packing area
        n_shelf = 6
        regions.append(list(itertools.product(range(start_charging_station_x, start_charging_station_x + charging_station_width_x), range(0, charging_station_length_y)))) 
        for i in range(n_shelf):
            regions.append(list(itertools.product([charging_station_width_x + first_shelf_to_charging_station_x + 
                                                    i * (shelf_width_x + inter_shelf_x) - 1,
                                                    charging_station_width_x + first_shelf_to_charging_station_x + 
                                                    i * (shelf_width_x + inter_shelf_x) + shelf_width_x], 
                                                range(charging_station_length_y + first_shelf_to_charging_station_y,
                                                    charging_station_length_y + first_shelf_to_charging_station_y + shelf_length_y))))
            
            
        regions.append(list(itertools.product(range(charging_station_width_x + first_shelf_to_charging_station_x + 
                                                    (n_shelf - 1) * (shelf_width_x + inter_shelf_x) + shelf_width_x + depot_to_last_shelf_x,
                                                        charging_station_width_x + first_shelf_to_charging_station_x +
                                                    (n_shelf - 1) * (shelf_width_x + inter_shelf_x) + shelf_width_x + depot_to_last_shelf_x + depot_width_x),
                                            range(0, depot_length_y))))

        return regions

    def allocate_obstacle_dars(self):
        obstacles = []
        # ICRA
        shelf_width_x = 2
        shelf_length_y = 5
        charging_station_width_x = 4
        charging_station_length_y = 6
        first_shelf_to_charging_station_x = 2
        first_shelf_to_charging_station_y = 2
        inter_shelf_x = 3
        
        # p0 charging station
        # p1 grocery p2 health p3 outdors p4 pet p5 furniture p6 electronics
        n_shelf = 6
        for i in range(n_shelf):
            obstacles.append(list(itertools.product(range(charging_station_width_x + first_shelf_to_charging_station_x + 
                                                        i * (shelf_width_x + inter_shelf_x),
                                                        charging_station_width_x + first_shelf_to_charging_station_x + 
                                                        i * (shelf_width_x + inter_shelf_x) + shelf_width_x), 
                                                  range(charging_station_length_y + first_shelf_to_charging_station_y,
                                                        charging_station_length_y + first_shelf_to_charging_station_y + shelf_length_y))))
            

        return obstacles

    # def initialize(self):
    #     # TRO version 1
    #     # type_robot_location = {(1, 0): (7, 0), (1, 1): (7, 1), (1, 2): (8, 1),
    #     #                        (2, 0): (6, 0), (2, 1): (6, 1)}
    #     # TRO version 2
    #     type_robot_location = {(1, 0): (8, 0), (1, 1): (8, 1), (1, 2): (9, 1),
    #                            (2, 0): (8, 9), (2, 1): (9, 9)}
    #     return type_robot_location

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
        # for action, preconds_effs in self.domain.get('robot_actions').items():
        #     for preconds in preconds_effs['preconditions']:
        #         if all(element in aps for element in preconds if "!" not in element) and \
        #             all(element[1:] not in aps for element in preconds if "!" in element):
        #             man_actions.append(action)
        for succ in self.action_model.succ[action_state]:
            man_actions.append((self.action_model.edges[(action_state, succ)]['label'], succ))
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
        return "supermarket"