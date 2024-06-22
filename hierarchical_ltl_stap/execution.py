import copy
from .util import prYellow, prRed
import numpy as np

def generate_simultaneous_exec(optimal_path, workspace, leaf_spec_order, args, simultaneous=True):
    if simultaneous:
        # Divide the optimal path into several segments corresponding to the phis
        # such that each segment only contains active robots that fulfill the phi.
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
            for curr_phi, robot_path_act in robot_path_act_per_phi:
                prYellow(f"{curr_phi}, {robot_path_act}")
            
        ordered_phis = [phi for phi, _ in robot_path_act_per_phi] # phi in ordered_phis are at least as important as those phis that are behind it
        robot_path_act = {type_robot: [(workspace.type_robot_location[type_robot], 'default')] for type_robot in workspace.type_robot_location.keys()}
        robot_phi = {type_robot: [''] for type_robot in workspace.type_robot_location.keys()}
        phi_horizon = [0] * len(ordered_phis) # the latest time step when the specific phi is involved 
        # robot_horizon = {type_robot: 1 for type_robot in workspace.type_robot_location.keys()}
        for idx in range(len(ordered_phis)):
            curr_phi = ordered_phis[idx]
            # first phi
            # no need to consider other stuff, just parallel the path 
            if idx == 0:
                for robot, path in robot_path_act_per_phi[idx][1].items():
                    for wpt_act in path:
                        # remove identical x
                        if wpt_act[0] != robot_path_act[robot][-1][0] or wpt_act[1] not in non_essential_actions:
                            robot_path_act[robot].append(wpt_act)
                            robot_phi[robot].append(curr_phi)
                    phi_horizon[idx] = max(phi_horizon[idx], len(robot_path_act[robot]))
                continue
                
            # (1) For each robot, find the phi that is the closest one behind (including) the current robot path
            # (2) Then between this phi and the final phi, determine the phi such that the robot must take action behind it
            # (3) Finally, add the robot path behind the time stamp determined by the phi
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
                    
                horizon_of_closest_pred_phi = -1
                for pre_phi_idx in range(idx-1, aligned_phi_idex - 1, -1): 
                    pre_phi = ordered_phis[pre_phi_idx]
                    pre_phi_prior_to_current_phi = curr_phi in leaf_spec_order[pre_phi]
                    current_phi_to_prior_pre_phi = pre_phi in leaf_spec_order[curr_phi]
                    is_independent = pre_phi_prior_to_current_phi and current_phi_to_prior_pre_phi
                    if not is_independent or ordered_phis[pre_phi_idx] == curr_phi:
                        horizon_of_closest_pred_phi = max(phi_horizon[pre_phi_idx], horizon_of_closest_pred_phi)
                # align
                tmp_x_act = (robot_path_act[robot][-1][0], 'default')
                robot_path_act[robot].extend([tmp_x_act] * (horizon_of_closest_pred_phi - len(robot_path_act[robot])))
                robot_phi[robot].extend([''] * (horizon_of_closest_pred_phi - len(robot_phi[robot])))
                # concatenate
                for wpt_act in path:
                    # remove identical x
                    if wpt_act[0] != robot_path_act[robot][-1][0] or wpt_act[1] not in non_essential_actions:
                        robot_path_act[robot].append(wpt_act)
                        robot_phi[robot].append(curr_phi)
                phi_horizon[idx] = max(phi_horizon[idx], len(robot_path_act[robot]))
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

def event_based_execution(robot_path_ori, robot_phi, robot_act_ori, leaf_spec_order, first_spec_candidates):
    current_exec_subtasks = []
    current_exec_robots = []
    current_exec_phis = []
    current_exec_act= []
   
    robot_path = copy.deepcopy(robot_path_ori)
    robot_act = copy.deepcopy(robot_act_ori)
    prRed(f"{robot_path}")
    prRed(f"{robot_phi}")
    prRed(f"{robot_act}")
    # init
    for robot, path in robot_path.items():
        # send init state
        path.pop(0)
        robot_phi[robot].pop(0)
        robot_act[robot].pop(0)

    # determine cuurent exec robots
    for first_spec in first_spec_candidates:
        for robot, tmp_phi in robot_phi.items():
            if tmp_phi and tmp_phi[0] == first_spec:
                current_exec_robots.append(robot)
                current_exec_subtasks.append(robot_path[robot][0])
                current_exec_phis.append(robot_phi[robot][0])
                current_exec_act.append(robot_act[robot][0])
                robot_path[robot].pop(0)
                robot_phi[robot].pop(0)
                robot_act[robot].pop(0)
    # send
    prRed(f"current_exec_robots: {current_exec_robots}")
    prRed(f"current_exec_subtasks: {current_exec_subtasks}")
    prRed(f"current_exec_phis: {current_exec_phis}")
    prRed(f"current_exec_act: {current_exec_act}")
    
    invalid_str = "-1"
    finished_task_str = invalid_str
    while current_exec_robots:
        # receive
        while finished_task_str == invalid_str:
            finished_task_str = input("Finished task: ")
            if (int(finished_task_str[0]), int(finished_task_str[2])) not in current_exec_robots:
                finished_task_str = invalid_str
            else:
                finished_robot = (int(finished_task_str[0]), int(finished_task_str[2]))
        finished_task_str = invalid_str
        prRed(f"finished robot {finished_robot}")
        # determine next subtask
        robot_idx = current_exec_robots.index(finished_robot)
        current_exec_robots.pop(robot_idx)
        current_exec_phis.pop(robot_idx)
        current_exec_subtasks.pop(robot_idx)
        current_exec_act.pop(robot_idx)
        for robot, path in robot_path.items():
            # robot is executing task
            if robot in current_exec_robots:
                continue
            if not path:
                continue
            tmp_phi = robot_phi[robot][0]
            while not tmp_phi and len(path)>0:
                path.pop(0)
                robot_phi[robot].pop(0)
                robot_act[robot].pop(0)
                if not path:
                    print("robot",robot,"if not path:")
                    continue
                tmp_phi = robot_phi[robot][0]
                print("robot",robot,"if not tmp_phi:")
            if not path:
                print("robot",robot,"if not path:")
                continue
            
            # find the existence of current phi prior to tmp_phi
            current_subtask_prior_to_phi = False
            for current_phi in current_exec_phis:
                if current_phi != tmp_phi and tmp_phi in leaf_spec_order[current_phi] and \
                    current_phi not in leaf_spec_order[tmp_phi]:
                        current_subtask_prior_to_phi = True
                        break
            if current_subtask_prior_to_phi:
                continue
            
            # find the existence of future phi prior to tmp_phi
            future_subtask_prior_to_phi = False
            for other_robot, future_phis in robot_phi.items():
                if other_robot == robot or not future_phis:
                    continue
                future_phi = future_phis[0]
                if future_phi and future_phi != tmp_phi and tmp_phi in leaf_spec_order[future_phi] and \
                    future_phi not in leaf_spec_order[tmp_phi]:
                        future_subtask_prior_to_phi = True
                        break
            if future_subtask_prior_to_phi:
                continue
            
            # send message robot, wpt, act
            current_exec_robots.append(robot)
            current_exec_subtasks.append(path[0])
            current_exec_phis.append(robot_phi[robot][0])
            current_exec_act.append(robot_act[robot][0])
            path.pop(0)
            robot_phi[robot].pop(0)
            robot_act[robot].pop(0)
        prRed(f"current_exec_robots: {current_exec_robots}")
        prRed(f"current_exec_subtasks: {current_exec_subtasks}")
        prRed(f"current_exec_phis: {current_exec_phis}")
        prRed(f"current_exec_act: {current_exec_act}")
            

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
    def plan_summary(self):
        robots_step_cost=[]
        num_robots=len(self.robot_path.keys())
        for key in self.robot_path.keys():
            curr_robot_path=self.robot_path[key]
            count=0
            curr_pos=curr_robot_path[0]
            for pos in curr_robot_path[1:]:
                count+=np.sum(np.abs(np.array(curr_pos)-np.array(pos)))
                curr_pos=pos
            robots_step_cost.append(int(count))
        return robots_step_cost
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
        # for robot_idx in self.current_exec_robots:
        #     if robot_idx in finished_robot:
            # 增加这个for循环用来支持对一次有若干任务同时结束的情况
            prRed(f"finished robot {finished_robot[idx]}")
            # determine next subtask
            # 如果有执行完的，就全部pop
            robot_idx = self.current_exec_robots.index(finished_robot[idx])
            self.current_exec_robots.pop(robot_idx)
            self.current_exec_phis.pop(robot_idx)
            self.current_exec_subtasks.pop(robot_idx)
            self.current_exec_act.pop(robot_idx)

        # 遍历每一个robot，是不是当前的robot，如果这个机器人正在执行，就不进行下一个动作
        for robot, path in self.robot_path.items():
            # robot is executing task
            if robot in self.current_exec_robots:
                print("robot",robot,"if robot in self.current_exec_robots:")
                continue
            if not path:
                print("robot",robot,"if not path:")
                continue
            tmp_phi = self.robot_phi[robot][0]
            while not tmp_phi and len(path)>0:
                path.pop(0)
                self.robot_phi[robot].pop(0)
                self.robot_act[robot].pop(0)
                if not path:
                    print("robot",robot,"if not path:")
                    continue
                tmp_phi = self.robot_phi[robot][0]
                print("robot",robot,"if not tmp_phi:")
            if not path:
                print("robot",robot,"if not path:")
                continue
            # if not tmp_phi:
            #     for key in self.robot_phi.keys():
            #         print(key,len(self.robot_phi[key]),self.robot_phi[key])
            #     print("robot",robot,"if not tmp_phi:")
            #     continue

            
            # find the existence of current phi prior to tmp_phi
            # 如果要执行 leaf_spec_order 就是 tmp_phi
            # 当前正在执行的且没执行完，并且要在tmpphi前执行，就先不执行tmpphi
            current_subtask_prior_to_phi = False
            for current_phi in self.current_exec_phis:
                if current_phi != tmp_phi and tmp_phi in self.leaf_spec_order[current_phi] and \
                    current_phi not in self.leaf_spec_order[tmp_phi]:
                        current_subtask_prior_to_phi = True
                        break
            if current_subtask_prior_to_phi:
                print("robot",robot,"if current_subtask_prior_to_phi:")
                continue
            
            # find the existence of future phi prior to tmp_phi
            # 找未执行的任务是不是要在tmpphi前执行，如果他们没被执行，那tmp就不能执行
            future_subtask_prior_to_phi = False
            for other_robot, future_phis in self.robot_phi.items():
                if other_robot == robot or not future_phis:
                    print("robot",robot,"if other_robot == robot or not future_phis:")
                    continue
                future_phi = future_phis[0]
                if future_phi and future_phi != tmp_phi and tmp_phi in self.leaf_spec_order[future_phi] and \
                    future_phi not in self.leaf_spec_order[tmp_phi]:
                        future_subtask_prior_to_phi = True
                        break
            if future_subtask_prior_to_phi:
                print("robot",robot,"if future_subtask_prior_to_phi:")
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
        print("(self.new_exec_robots,self.new_exec_subtasks,self.new_exec_phis,self.new_exec_act     )",(self.new_exec_robots,self.new_exec_subtasks,self.new_exec_phis,self.new_exec_act     ))
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
        