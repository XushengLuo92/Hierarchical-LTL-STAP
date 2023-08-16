# -*- coding: utf-8 -*-

from random import randint
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import random
import sys
import itertools
import pickle
import copy


class Workspace(object):
    """
    define the workspace where robots reside
    """
    def __init__(self):
        # dimension of the workspace
        # self.length = int(sys.argv[1])
        # self.width = int(sys.argv[1])
        # n = int(sys.argv[2])
        self.length = 15 # 9   # length
        self.width = 40 # 9   # width
        # n = 4
        self.type_num = {1: 2, 2: 2, 3: 2}   # single-task robot
        self.workspace = (self.length, self.width)
        self.num_of_regions = 8
        self.num_of_obstacles = 6
        self.occupied = []
        self.regions = {'p{0}'.format(i): j for i, j in enumerate(self.allocate_region_dars())}
        self.obstacles = {'o{0}'.format(i+1): j for i, j in enumerate(self.allocate_obstacle_dars())}
        self.type_robot_location = self.initialize()
        # customized location
        # self.type_robot_location[(2, 0)]  = (0, 0) # nav task 4
        # region and corresponding locations
        self.label_location = {'r{0}'.format(i + 1): j for i, j in enumerate(list(self.type_robot_location.values()))}
        # region where robots reside
        self.type_robot_label = dict(zip(self.type_robot_location.keys(), self.label_location.keys()))
        # atomic proposition
        self.atomic_prop = self.get_atomic_prop()

        self.graph_workspace = nx.Graph()
        self.build_graph()

        self.p2p = self.point_to_point_path()  # label2label path

    def reachable(self, location, obstacles):
        next_location = []
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

    def plot_workspace(self):
        ax = plt.figure(1).gca()
        ax.set_xlim((0, self.width))
        ax.set_ylim((0, self.length))
        plt.xticks(np.arange(0, self.width + 1, 1.0))
        plt.yticks(np.arange(0, self.length + 1, 1.0))
        # self.plot_workspace_helper(ax, self.regions, 'region')
        self.plot_workspace_helper(ax, self.obstacles, 'obstacle')
        for index, i in self.type_robot_location.items():
            plt.plot(i[0] + 0.5, i[1] + 0.5, 'o')
            ax.text(i[0] + 0.5, i[1] + 0.5, r'${}$'.format(index), fontsize=10)

    def plot_workspace_helper(self, ax, obj, obj_label):
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(which='major', color='k', linestyle='--')
        for key in obj:
            color = 'b' if obj_label != 'region' else 'c'
            for grid in obj[key]:
                x_ = grid[0]
                y_ = grid[1]
                x = []
                y = []
                patches = []
                for point in [(x_, y_), (x_ + 1, y_), (x_ + 1, y_ + 1), (x_, y_ + 1)]:
                    x.append(point[0])
                    y.append(point[1])
                polygon = Polygon(np.column_stack((x, y)), True)
                patches.append(polygon)
                p = PatchCollection(patches, facecolors=color, edgecolors=color, alpha=0.4)
                ax.add_collection(p)
            ax.text(np.mean(x) - 0.2, np.mean(y) - 0.2, r'${}_{{{}}}$'.format(key[0], key[1:]), fontsize=8)

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