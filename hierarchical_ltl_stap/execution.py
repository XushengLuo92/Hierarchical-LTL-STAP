import copy
from .util import prYellow, prRed

def generate_simultaneous_exec(optimal_path, workspace, leaf_spec_order, args, simultaneous=True):
    if simultaneous:
        # only include active robots per phi
        # it is possible that the path for a phi is interrupted 
        non_essential_actions = ['default', 'in-spec', 'inter-spec-i', 'inter-spec-ii']
        robot_path_act_per_phi = [] 
        temp_robot_path_act = dict()
        pre_phi = ''
        for wpt_act in optimal_path:
            if args.print_path:
                prRed(wpt_act)
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
        if args.print_path:
            for phi, robot_path_act in robot_path_act_per_phi:
                prYellow(f"{phi}, {robot_path_act}")
            
        ordered_phis = [phi for phi, _ in robot_path_act_per_phi]
        robot_path_act = {type_robot: [(workspace.type_robot_location[type_robot], 'default')] for type_robot in workspace.type_robot_location.keys()}
        robot_phi = {type_robot: [''] for type_robot in workspace.type_robot_location.keys()}
        phi_horizon = [0] * len(ordered_phis)
        # robot_horizon = {type_robot: 1 for type_robot in workspace.type_robot_location.keys()}
        for idx in range(len(ordered_phis)):
            phi = ordered_phis[idx]
            # first phi
            if idx == 0:
                for robot, path in robot_path_act_per_phi[idx][1].items():
                    for wpt_act in path:
                        # remove identical x
                        if wpt_act[0] != robot_path_act[robot][-1][0] or wpt_act[1] not in non_essential_actions:
                            robot_path_act[robot].append(wpt_act)
                            robot_phi[robot].append(phi)
                    phi_horizon[idx] = max(phi_horizon[idx], len(robot_path_act[robot]))
                continue
                
            # for each robot, find the phi that the robot is aligned, that is, the horizon of robot path lies within the duration of the aligned phi
            # loop backwards until the aligned phi, stop early if reaching the phi that has the precedent relation
            for robot, path in robot_path_act_per_phi[idx][1].items():
                specific_robot_horizon = len(robot_path_act[robot])
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
                for pre_phi_idx in range(idx-1, aligned_phi_idex - 1, -1): 
                    pre_phi = ordered_phis[pre_phi_idx]
                    pre_phi_prior_phi = phi in leaf_spec_order[pre_phi]
                    phi_prior_pre_phi = pre_phi in leaf_spec_order[phi]
                    is_independent = pre_phi_prior_phi and phi_prior_pre_phi
                    if not is_independent and ordered_phis[pre_phi_idx] != phi:
                        horizon_including_pre_phi = phi_horizon[pre_phi_idx]
                        # align
                        tmp_x_act = (robot_path_act[robot][-1][0], 'default')
                        robot_path_act[robot].extend([tmp_x_act] * (horizon_including_pre_phi - len(robot_path_act[robot])))
                        robot_phi[robot].extend([robot_phi[robot][-1]] * (horizon_including_pre_phi - len(robot_phi[robot])))
                        # concatenate
                        for wpt_act in path:
                            # remove identical x
                            if wpt_act[0] != robot_path_act[robot][-1][0] or wpt_act[1] not in non_essential_actions:
                                robot_path_act[robot].append(wpt_act)
                                robot_phi[robot].append(phi)
                        # robot_horizon[robot] = horizon_including_pre_phi + horizon_per_robot_aligned_phi
                        phi_horizon[idx] = max(phi_horizon[idx], len(robot_path_act[robot]))
                    elif pre_phi_idx == aligned_phi_idex or ordered_phis[pre_phi_idx] == phi:
                        # reaching all the way down to the aligned phi and independent of the aligned phi
                        # or same robot and same phi
                        # concatenate
                        for wpt_act in path:
                            # remove identical x
                            if wpt_act[0] != robot_path_act[robot][-1][0] or wpt_act[1] not in non_essential_actions:
                                robot_path_act[robot].append(wpt_act)
                                robot_phi[robot].append(phi)
                        # robot_horizon[robot] = horizon_including_pre_phi + horizon_per_robot_aligned_phi
                        phi_horizon[idx] = max(phi_horizon[idx],len(robot_path_act[robot]))
                    elif is_independent:
                        # independent
                        continue
                    else:
                        exit
    else:
        robot_path_act = {type_robot: [] for type_robot in workspace.type_robot_location.keys() }
        pre_phi = ''
        for wpt_act in optimal_path:
            if pre_phi and wpt_act.phi != pre_phi:
                for robot, path in robot_path_act.items():
                    if not path:
                        path.append(workspace.type_robot_location[robot])
                horizon = max([len(path) for path in robot_path_act.values()])
                for path in robot_path_act.values():
                    path.extend((horizon - len(path)) * [path[-1]])
                    # prRed(path)
            
            # prYellow(wpt)
            pre_phi = wpt_act.phi
            type_robot = wpt_act.type_robot
            x_act = wpt_act.type_robots_x[type_robot]
            robot_path_act[type_robot].append(x_act)

    horizon = max([len(path) for path in robot_path_act.values()])
    for robot, path in robot_path_act.items():
        path_len = len(path)
        if not path:
            path.extend((horizon - path_len) * [(workspace.type_robot_location[robot], 'default')])
            robot_phi[robot].extend((horizon - path_len) * [robot_phi[robot]])
        else:
            tmp_x_act = (path[-1][0], 'default')
            path.extend((horizon - path_len) * [tmp_x_act])
            robot_phi[robot].extend((horizon - path_len) * [robot_phi[robot][-1]])
        # prRed(path)
    
    robot_path = {type_robot: [x_act[0] for x_act in path_act] for type_robot, path_act in robot_path_act.items()}
    robot_act = {type_robot: [x_act[1] for x_act in path_act] for type_robot, path_act in robot_path_act.items()}
    return robot_path, robot_phi, robot_act
class eventExec():
    # modified xsj
    # change the interaction methods from hand in input into a request-respond way
    def __init__(self,robot_path_ori, robot_phi, robot_act_ori, leaf_spec_order, first_spec_candidates,type='no interact') -> None:
        pass
        self.whole_task_finished:bool=False
        self.current_exec_subtasks = []
        self.current_exec_robots = []
        self.current_exec_phis = []
        self.current_exec_act= []
        self.invalid_str = "-1"

        self.new_exec_subtasks = []
        self.new_exec_robots = []
        self.new_exec_phis = []
        self.new_exec_act= []

        self.robot_phi=robot_phi
        self.robot_path = copy.deepcopy(robot_path_ori)
        self.robot_act = copy.deepcopy(robot_act_ori)
        prRed(f"{self.robot_path}")
        prRed(f"{self.robot_phi}")
        prRed(f"{self.robot_act}")

        self.leaf_spec_order=leaf_spec_order
        self.first_spec_candidates=first_spec_candidates
        if type=='no interact':
            self.event_based_execution_no_interaction()
        else:
            # otherwise arbitary
            pass
            # self.event_based_execution_init()
        
    def event_based_execution_init(self):

        # init
        for robot, path in self.robot_path.items():
            # send init state
            path.pop(0)
            self.robot_phi[robot].pop(0)
            self.robot_act[robot].pop(0)

        # determine cuurent exec robots
        for first_spec in self.first_spec_candidates:
            for robot, tmp_phi in self.robot_phi.items():
                if tmp_phi and tmp_phi[0] == first_spec:
                    self.new_exec_robots.append(robot)
                    self.new_exec_subtasks.append(self.robot_path[robot][0])
                    self.new_exec_phis.append(self.robot_phi[robot][0])
                    self.new_exec_act.append(self.robot_act[robot][0])

                    self.robot_path[robot].pop(0)
                    self.robot_phi[robot].pop(0)
                    self.robot_act[robot].pop(0)
        # send
        self.current_exec_subtasks = copy.deepcopy(self.new_exec_subtasks)
        self.current_exec_robots = copy.deepcopy(self.new_exec_robots)
        self.current_exec_phis = copy.deepcopy(self.new_exec_phis)
        self.current_exec_act= copy.deepcopy(self.new_exec_act)

        prRed(f"current_exec_robots: {self.current_exec_robots}")
        prRed(f"current_exec_subtasks: {self.current_exec_subtasks}")
        prRed(f"current_exec_phis: {self.current_exec_phis}")
        prRed(f"current_exec_act: {self.current_exec_act}")
        if self.current_exec_robots:
            self.whole_task_finished=False
        else:
            self.whole_task_finished=True
        return self.whole_task_finished,(self.new_exec_robots,self.new_exec_subtasks,self.new_exec_phis,self.new_exec_act)
    
    def event_based_execution_request_new(self,finished_robot:list[(int,int)]):
        self.new_exec_subtasks = []
        self.new_exec_robots = []
        self.new_exec_phis = []
        self.new_exec_act= []

        for idx in range(len(finished_robot)):
            # 增加这个for循环用来支持对一次有若干任务同时结束的情况
            prRed(f"finished robot {finished_robot[idx]}")
            # determine next subtask
            robot_idx = self.current_exec_robots.index(finished_robot[idx])
            self.current_exec_robots.pop(robot_idx)
            self.current_exec_phis.pop(robot_idx)
            self.current_exec_subtasks.pop(robot_idx)
            self.current_exec_act.pop(robot_idx)


            for robot, path in self.robot_path.items():
                # robot is executing task
                if robot in self.current_exec_robots:
                    continue
                if not path:
                    continue
                tmp_phi = self.robot_phi[robot][0]
                if not tmp_phi:
                    continue
                
                # find the existence of current phi prior to tmp_phi
                current_subtask_prior_to_phi = False
                for current_phi in self.current_exec_phis:
                    if current_phi != tmp_phi and tmp_phi in self.leaf_spec_order[current_phi] and \
                        current_phi not in self.leaf_spec_order[tmp_phi]:
                            current_subtask_prior_to_phi = True
                            break
                if current_subtask_prior_to_phi:
                    continue
                
                # find the existence of future phi prior to tmp_phi
                future_subtask_prior_to_phi = False
                for other_robot, future_phis in self.robot_phi.items():
                    if other_robot == robot or not future_phis:
                        continue
                    future_phi = future_phis[0]
                    if future_phi and future_phi != tmp_phi and tmp_phi in self.leaf_spec_order[future_phi] and \
                        future_phi not in self.leaf_spec_order[tmp_phi]:
                            future_subtask_prior_to_phi = True
                            break
                if future_subtask_prior_to_phi:
                    continue
                
                # send message robot, wpt, act
                self.current_exec_robots.append(robot)
                self.current_exec_subtasks.append(path[0])
                self.current_exec_phis.append(self.robot_phi[robot][0])
                self.current_exec_act.append(self.robot_act[robot][0])

                self.new_exec_subtasks.append(path[0])
                self.new_exec_robots.append(robot)
                self.new_exec_phis.append(self.robot_phi[robot][0])
                self.new_exec_act.append(self.robot_act[robot][0])

                path.pop(0)
                self.robot_phi[robot].pop(0)
                self.robot_act[robot].pop(0)
        prRed(f"current_exec_robots: {self.current_exec_robots}")
        prRed(f"current_exec_subtasks: {self.current_exec_subtasks}")
        prRed(f"current_exec_phis: {self.current_exec_phis}")
        prRed(f"current_exec_act: {self.current_exec_act}")
        if self.current_exec_robots:
            self.whole_task_finished=False
        else:
            self.whole_task_finished=True
        return self.whole_task_finished,(self.new_exec_robots,self.new_exec_subtasks,self.new_exec_phis,self.new_exec_act     )
        
    def event_based_execution_no_interaction(self):
        self.event_based_execution_init()
        finished_task_str = self.invalid_str
        while self.current_exec_robots:
            while finished_task_str == self.invalid_str:
                finished_task_str = input("Finished task: ")
                if (int(finished_task_str[0]), int(finished_task_str[2])) not in self.current_exec_robots:
                    finished_task_str = self.invalid_str
                else:
                    finished_robot = (int(finished_task_str[0]), int(finished_task_str[2]))
            finished_task_str = self.invalid_str
            self.event_based_execution_request_new([finished_robot])
        