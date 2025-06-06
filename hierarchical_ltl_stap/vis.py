import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import matplotlib.animation as anim
import matplotlib.patches as mpatches
from .util import plot_workspace

class RobotPath:
    def __init__(self, x, color, robot_path, robot_act, robot_pre_suf_time, workspace, ap):
        self.robot_path = robot_path
        self.robot_act = robot_act
        self.robot_pre_suf_time = robot_pre_suf_time
        self.i_x = np.asarray(x, dtype=float)
        self.color = np.asarray(color, dtype=float)
        self.x = self.i_x.copy()
        self.direction = self.i_x.copy() - self.i_x.copy()
        self.elapse_time = -3  # adjust this number to display time recorder from 0s
        self.dt = 1
        self.workspace = workspace
        self.ap = ap
        self.sat = dict()

    def iterate(self):
        robot_point = {}
        self.elapse_time += self.dt
        elapse_time = self.elapse_time
        x = []
        direction = []
        act = []
        non_essential_actions = ['default', 'in-spec', 'inter-spec-i', 'inter-spec-ii']
        for type_robot, path in self.robot_path.items():
            if elapse_time >= len(path) - 1:
                # robot stays put
                if round(self.robot_pre_suf_time[type_robot][0]) == round(self.robot_pre_suf_time[type_robot][1]):
                    x.append((path[-1][0]+0.5, path[-1][1]+0.5))
                    direction.append((0, 0))
                    a = self.robot_act[type_robot][-1]
                else:
                    t = (int(np.floor(elapse_time)) - self.robot_pre_suf_time[type_robot][0]) % \
                    (self.robot_pre_suf_time[type_robot][1] - self.robot_pre_suf_time[type_robot][0])
                    first = self.robot_path[type_robot][self.robot_pre_suf_time[type_robot][0]+t]
                    second = self.robot_path[type_robot][self.robot_pre_suf_time[type_robot][0]+t+1]
                    x.append((first[0]+(second[0]-first[0]) * (elapse_time - np.floor(elapse_time)) + 0.5,
                              first[1]+(second[1]-first[1]) * (elapse_time - np.floor(elapse_time)) + 0.5))
                    direction.append((second[0] - first[0], second[1] - first[1]))
                    a = self.robot_act[type_robot][int(np.floor(elapse_time))]
            else:
                first = self.robot_path[type_robot][int(np.floor(elapse_time))]
                second = self.robot_path[type_robot][int(np.floor(elapse_time)+1)]
                x.append((first[0] + (second[0] - first[0]) * (elapse_time - np.floor(elapse_time)) + 0.5,
                          first[1] + (second[1] - first[1]) * (elapse_time - np.floor(elapse_time)) + 0.5))
                direction.append((second[0] - first[0], second[1] - first[1]))
              
                a = self.robot_act[type_robot][int(np.floor(elapse_time))]
            
            if a not in non_essential_actions:
                act.append(f'({type_robot[1]} {a})')

            robot_point[type_robot] = x[-1]
        self.x = np.array(x)
        self.direction = np.array(direction)
        return act
        # self.label(robot_point)

    def label(self, robot_point):
        true_ap = dict()
        # loop over each conjunction in the task formula
        for aps in self.ap:
            sat = True
            robot = []
            for ap in aps:
                # robot of certain type that visits the specified region
                r = [type_robot[1]+1 for type_robot, location in robot_point.items() if type_robot[0] == ap[1]
                     and (location[0]-0.5, location[1]-0.5) == self.workspace.regions[ap[0]]]
                # whether the conjunction is satisfied
                if len(r) < ap[2]:
                    sat = False
                    break
                robot.append(r)
            if sat:
                # (location, type): #robots
                true_ap.update({(ap[0], ap[1]): robot[index] for index, ap in enumerate(aps)})

        if true_ap and self.elapse_time != -1:
            self.sat = true_ap

def animate(i, ax, particles, quiver, annots, cls_robot_path, time_template, time_text, ap_template, ap_text):
    act = cls_robot_path.iterate()
    time_text.set_text(time_template % cls_robot_path.elapse_time)
    # ap_text.set_text(ap_template % cls_robot_path.)
    for t, new_x_i, new_y_i in zip(annots, cls_robot_path.x[:, 0], cls_robot_path.x[:, 1]):
        t.set_position((new_x_i, new_y_i+0.1))

    particles.set_offsets(cls_robot_path.x)
    particles.set_array(cls_robot_path.color)
    quiver.set_offsets(cls_robot_path.x)
    quiver.set_UVC(cls_robot_path.direction[:, 0], cls_robot_path.direction[:, 1])
    # for ap, location_type, robot in zip(ap_text[:len(cls_robot_path.sat.keys())], cls_robot_path.sat.keys(),
    #                                     cls_robot_path.sat.values()):
    #     ap.set_text(ap_template.format(robot, 'of type {0}'.format(location_type[1]),
    #                                    'visit {0}'.format(location_type[0][1:])))
    # for ap in ap_text[len(cls_robot_path.sat.keys()):]:
    #     ap.set_text(ap_template.format('{0}'.format("."), '{0}'.format("."), '{0}'.format(".")))
    ap_text.set_text(ap_template.format('{0}'.format('; '.join(act))))
    return [particles]+[quiver]+annots+[time_text]+[ap_text]
            
def vis(task, case, workspace, robot_path, robot_pre_suf_time, ap, robot_act):
    num_type = len(workspace.type_num.keys())
    colors_type = np.linspace(0.9, 0.1, num_type)
    # color = [0.4, 0.6]
    x = list((value[0]+0.5, value[1]+0.5) for value in workspace.type_robot_location.values())
    colors = [colors_type[i[0]-1] for i in robot_path.keys()]

    cls_robot_path = RobotPath(x, colors, robot_path, robot_act, robot_pre_suf_time, workspace, ap)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax.yaxis.tick_right()
    plot_workspace(workspace, ax)

    time_template = 'time = %.1fs'
    time_text = ax.text(0.01, 1.05, time_template % cls_robot_path.elapse_time, transform=ax.transAxes)
    
    ap_template = '{0}'
    ap_text = ax.text(0.5, 1.05, ap_template.format('{0}'.format(".")), color='red', weight='bold',  transform=ax.transAxes)
    cls_robot_path.label(workspace.type_robot_location)
    groups = ["type1", "type2", "type3"]
    particles = ax.scatter(cls_robot_path.x[:, 0], cls_robot_path.x[:, 1], c=cls_robot_path.color, s=30, cmap="hsv", vmin=0, vmax=1)
    quiver = ax.quiver(cls_robot_path.x[:, 0], cls_robot_path.x[:, 1], 
                       cls_robot_path.direction[:, 0], cls_robot_path.direction[:, 1],
                       scale=25, width=0.004, color="r")
    # Create a legend patch for each group
    # legend_patches = [mpatches.Patch(color=plt.cm.hsv(color), label=group) for group, color in zip(groups, colors_type)]
    # legend_patches = []
    # Add the legend patches to the plot
    # ax.legend(handles=legend_patches, fontsize=6)
    # annots = [ax.text(100, 100, r"[{0},{1}]".format(type_robot[1]+1, type_robot[0]), weight='bold', fontsize=8)
    #           for type_robot in robot_path.keys()]
    annots = [ax.text(100, 100, r"{0}".format(type_robot[1]), weight='bold', fontsize=8)
              for type_robot in robot_path.keys()]

    max_frame = max(2 * time[1] - time[0] for time in robot_pre_suf_time.values())/cls_robot_path.dt + 1
    ani = anim.FuncAnimation(fig, animate, fargs=[ax, particles, quiver, annots, cls_robot_path, time_template, time_text,
                                                  ap_template, ap_text],
                             frames=int(np.ceil(max_frame)), interval=30, blit=True)
    ani.save(f'./data/stap_{task}_{case}.mp4', fps=2/cls_robot_path.dt, dpi=400)