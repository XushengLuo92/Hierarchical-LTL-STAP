from util import prYellow, prRed

def generate_simultaneous_exec(optimal_path, workspace, leaf_specs, leaf_spec_order, simultaneous=True):
    if simultaneous:
        # only include active robots per phi
        # it is possible that the path for a phi is interrupted 
        robot_path_per_phi = [] 
        temp_robot_path = dict()
        pre_phi = ''
        for wpt in optimal_path:
            prRed(wpt)
            if pre_phi and wpt.phi != pre_phi:
                robot_path_per_phi.append((pre_phi, temp_robot_path.copy()))
                temp_robot_path.clear()
            
            pre_phi = wpt.phi
            type_robot = wpt.type_robot
            x = wpt.type_robots_x[type_robot]
            # remove identical x
            if type_robot in temp_robot_path.keys() and x != temp_robot_path[type_robot][-1]:
                temp_robot_path[type_robot].append(x)
            elif type_robot not in temp_robot_path.keys():
                temp_robot_path[type_robot] = [x]
            
        robot_path_per_phi.append((pre_phi, temp_robot_path.copy()))
        for phi, robot_path in robot_path_per_phi:
            prYellow(f"{phi}, {robot_path}")
        
        ordered_phis = [phi for phi, _ in robot_path_per_phi]
        robot_path = {type_robot: [workspace.type_robot_location[type_robot]] for type_robot in workspace.type_robot_location.keys()}
        phi_horizon = [0] * len(ordered_phis)
        # robot_horizon = {type_robot: 1 for type_robot in workspace.type_robot_location.keys()}
        for idx in range(len(ordered_phis)):
            phi = ordered_phis[idx]
            # first phi
            if idx == 0:
                for robot, path in robot_path_per_phi[idx][1].items():
                    for wpt in path:
                        # remove identical x
                        if wpt != robot_path[robot][-1]:
                            robot_path[robot].append(wpt)
                    phi_horizon[idx] = max(phi_horizon[idx], len(robot_path[robot]))
                continue
                
            # for each robot, find the phi that the robot is aligned, that is, the horizon of robot path lies within the duration of the aligned phi
            # loop backwards until the aligned phi, stop early if reaching the phi that has the precedent relation
            for robot, path in robot_path_per_phi[idx][1].items():
                specific_robot_horizon = len(robot_path[robot])
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
                        robot_path[robot].extend([robot_path[robot][-1]] * (horizon_including_pre_phi - len(robot_path[robot])))
                        # concatenate
                        for wpt in path:
                            # remove identical x
                            if wpt != robot_path[robot][-1]:
                                robot_path[robot].append(wpt)
                        # robot_horizon[robot] = horizon_including_pre_phi + horizon_per_robot_aligned_phi
                        phi_horizon[idx] = max(phi_horizon[idx], len(robot_path[robot]))
                    elif pre_phi_idx == aligned_phi_idex or ordered_phis[pre_phi_idx] == phi:
                        # reaching all the way down to the aligned phi and independent of the aligned phi
                        # or same robot and same phi
                        # concatenate
                        for wpt in path:
                            # remove identical x
                            if wpt != robot_path[robot][-1]:
                                robot_path[robot].append(wpt)
                        # robot_horizon[robot] = horizon_including_pre_phi + horizon_per_robot_aligned_phi
                        phi_horizon[idx] = max(phi_horizon[idx],len(robot_path[robot]))
                    elif is_independent:
                        # independent
                        continue
                    else:
                        exit
    else:
        robot_path = {type_robot: [] for type_robot in workspace.type_robot_location.keys() }
        pre_phi = ''
        for wpt in optimal_path:
            if pre_phi and wpt.phi != pre_phi:
                for robot, path in robot_path.items():
                    if not path:
                        path.append(workspace.type_robot_location[robot])
                horizon = max([len(path) for path in robot_path.values()])
                for path in robot_path.values():
                    path.extend((horizon - len(path)) * [path[-1]])
                    # prRed(path)
            
            # prYellow(wpt)
            pre_phi = wpt.phi
            type_robot = wpt.type_robot
            x = wpt.type_robots_x[type_robot]
            robot_path[type_robot].append(x)

    horizon = max([len(path) for path in robot_path.values()])
    for robot, path in robot_path.items():
        if not path:
            path.extend((horizon - len(path)) * [workspace.type_robot_location[robot]])
        else:
            path.extend((horizon - len(path)) * [path[-1]])
        # prRed(path)
        
    return robot_path