import networkx as nx 
from util import vis_graph

class Specification():
    def __init__(self) -> None:
        self.hierarchy = []
    """_summary_
    """
    def get_task_specification(self, task, case):
        """_summary_

        Args:
            task (_type_): _description_
            case (_type_): _description_

        Returns:
            _type_: _description_
        """
        if task == "man":
            return self.get_manipulation_specification(case)
        elif task == "nav":
            return self.get_navigation_specification(case)
        else:
            exit
        
    def get_navigation_specification(self, case):
        """_summary_

        Args:
            case (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.hierarchy = []
        if case == 0:
            # ------------------------ task 0 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_2_1_0 || p200_1_1_0) && <> p300_1_1_0"
            self.hierarchy.append(level_one)

            level_two = dict()
            level_two["p100"] = "<> (p2_2_1_0 && <> p3_1_1_0)"
            level_two["p200"] = "<> p4_1_1_0"
            level_two["p300"] = "<> p5_1_1_0"
            # level_two["p300"] = "<> p1_1_1_0"
            self.hierarchy.append(level_two)
        elif case == 1: 
            # ------------------------ task 1 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_1_1_0 && <> p1_2_1_0)"
            self.hierarchy.append(level_one)

            level_two = dict()
            # level_two["p100"] = "<> p2_1_1_0"
            level_two["p100"] = "<> (p2_1_1_0 && <> p4_1_1_0)"
            self.hierarchy.append(level_two)
        elif case == 2: 
            # ------------------------ task 2 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_1_1_0 && <> p200_1_1_0)"
            self.hierarchy.append(level_one)

            level_two = dict()
            level_two["p100"] = "<> p2_1_1_0 && <> p4_1_1_0"
            level_two["p200"] = "<> (p3_1_1_0 && <> (p5_1_1_0 || p1_1_1_0))"
            self.hierarchy.append(level_two)
        elif case == 3: 
            # ------------------------ task 3 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_1_1_0 && <> (p200_1_1_0 && <> p7_1_1_0))"
            self.hierarchy.append(level_one)

            level_two = dict()
            level_two["p100"] = "<> (p2_2_1_0 && <> p4_1_1_0)"
            level_two["p200"] = "<> (p3_2_1_0 && <> (p5_1_1_0 || p1_1_1_0)) && <> p6_1_1_0 && !p6_1_1_0 U p3_2_1_0"
            self.hierarchy.append(level_two)
        elif case == 4: 
            # ------------------------ task 4 -------------------------
            level_one = dict()
            # level_one["p0"] = "<> (p3_2_1_0 && X(p3_2_1_0 U p3_1_1_0))" # && <> p3_1_1_0" # && <> p1_2_1_0"
            level_one["p0"] = "<> (p100_1_1_0 && <> p5_1_1_1))"
            self.hierarchy.append(level_one)

            level_two = dict()
            level_two["p100"] = "<> (p200_1_1_0 && <> p300_1_1_0)"
            self.hierarchy.append(level_two)
            
            level_three = dict()
            # level_three["p200"] = "<> p1_2_1_0 && !p2_2_1_0 U p1_2_1_0"
            level_three["p200"] = "<> (p3_2_1_1 && X (p3_2_1_1 U p3_1_1_1))"
            level_three['p300'] = "<> p1_2_1_1"
            self.hierarchy.append(level_three)
        elif case == 5:
            # task 1 in ICRA paper
            level_one = dict()
            level_one["p0"] = '<> p101_1_1_0 && <> p102_1_1_0'
            self.hierarchy.append(level_one)
            level_two = dict()
            # level_two['p101'] = '<> p6_3_1_3 && <> (p201_1_1_0 && <> p206_1_1_0 && <> (p202_1_1_0 && <> p203_1_1_0))'
            level_two['p101'] = '<> (p201_1_1_0 && <> p206_1_1_0 && <> (p202_1_1_0 && <> p203_1_1_0))'
            level_two['p102'] = '<> (p204_1_1_0 &&  <> p205_1_1_0)'
            self.hierarchy.append(level_two)
            level_three = dict()
            # p0 dock
            # p1 grocery p2 health p3 outdors p4 pet p5 furniture p6 electronics 
            # p7 packing area
            level_three['p201'] = '<> (p5_1_1_1 && X (p5_1_1_1 U p5_3_1_3))'
            level_three['p202'] = '<> p3_1_1_1 && <> p4_1_1_1'
            level_three['p203'] = '<> (p7_1_1_1 && <> p0_1_1_1)'
            level_three['p204'] = '<> p2_2_1_2 && <> p1_2_1_2 && !p1_2_1_2 U p2_2_1_2'
            level_three['p205'] = '<> (p7_2_1_2 && <> p0_2_1_2)'
            level_three['p206'] = '<> (p7_3_1_3 &&  <> p0_3_1_3)'
            self.hierarchy.append(level_three)
            # level_four = dict()
            # level_four['p301'] = '<> (p5_1_1_1 && X (p5_1_1_1 U p5_3_1_3))'
            # hierarchy.append(level_four)
        elif case == 6:
            # task 2 in ICRA paper
            # p0 dock
            # p1 grocery p2 health p3 outdors p4 pet p5 furniture p6 electronics 
            # p7 packing area
            level_one = dict()
            level_one["p0"] = '<> (p101_1_1_0 && <> (p102_1_1_0 && <> (p103_1_1_0 &&  <> p104_1_1_0)))'
            self.hierarchy.append(level_one)
            level_two = dict()
            level_two['p101'] = '<> p5_1_1_1 && <> p3_1_1_1'
            level_two['p102'] = '<> p2_1_1_1 && <> p1_1_1_1'
            level_two['p103'] = '<> p6_1_1_1 && <> p4_1_1_1'
            level_two['p104'] = '<> (p7_1_1_1 && <> p0_1_1_1)'
            self.hierarchy.append(level_two)
        elif case == 7:
            level_one = dict()
            level_one["p0"] = '<> (p101_1_1_0 && <> p102_1_1_0) && <> (p103_1_1_0 && <> p104_1_1_0)'
            self.hierarchy.append(level_one)
            level_two = dict()
            level_two['p101'] = '<> p2_1_1_1 && <> p1_1_1_1 && <> p6_1_1_1 && <> p4_1_1_1'
            level_two['p102'] = '<> (p7_1_1_1 && <> p0_1_1_1)'
            level_two['p103'] = '<> (p5_1_1_2 && X (p5_1_1_2 U p5_3_1_3))'
            level_two['p104'] = '<> (p3_1_1_2 && <> (p7_1_1_2 && <> p0_1_1_2)) && <>(p7_3_1_3 && <> p0_3_1_3)'
            self.hierarchy.append(level_two)
        elif case == 8:
            # task 3 in ICRA paper
            level_one = dict()
            level_one["p0"] = '<> (p101_1_1_0 && <> p102_1_1_0) && (<> p103_1_1_0 || <> p104_1_1_0)'
            # level_one["p0"] = '(<> p103_1_1_0 || <> p104_1_1_0)'
            self.hierarchy.append(level_one)
            level_two = dict()
            level_two['p101'] = '<> p2_1_1_1 && <> p1_1_1_1 && <> p6_1_1_1 && <> p4_1_1_1'
            level_two['p102'] = '<> (p7_1_1_1 && <> p0_1_1_1)'
            level_two['p103'] = '<> (p3_2_1_2 && <> (p7_2_1_2 && <> p0_2_1_2))'
            level_two['p104'] = '<> (p3_3_1_3 && <> (p7_3_1_3 && <> p0_3_1_3))'
            self.hierarchy.append(level_two)
        elif case == 9:
            level_one = dict()
            level_one["p0"] = '<> p1 && <> p2 && <> p3'
            self.hierarchy.append(level_one)
        return self.hierarchy
    
    def get_manipulation_specification(self, case):
        """_summary_

        Args:
            case (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.hierarchy = []
        if case == 0:
            # ------------------------ task 0 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_2_1_0 || p200_1_1_0) && <> p300_1_1_0"
            self.hierarchy.append(level_one)

            level_two = dict()
            level_two["p100"] = "<> (p2_2_1_0 && <> p3_1_1_0)"
            level_two["p200"] = "<> p4_1_1_0"
            level_two["p300"] = "<> p5_1_1_0"
            # level_two["p300"] = "<> p1_1_1_0"
            self.hierarchy.append(level_two)
        elif case == 1: 
            # ------------------------ task 1 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_1_1_0 && <> p1_2_1_0)"
            self.hierarchy.append(level_one)

            level_two = dict()
            # level_two["p100"] = "<> p2_1_1_0"
            level_two["p100"] = "<> (p2_1_1_0 && <> p4_1_1_0)"
            self.hierarchy.append(level_two)
        elif case == 2: 
            # ------------------------ task 2 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_1_1_0 && <> p200_1_1_0)"
            self.hierarchy.append(level_one)

            level_two = dict()
            level_two["p100"] = "<> p2_1_1_0 && <> p4_1_1_0"
            level_two["p200"] = "<> (p3_1_1_0 && <> (p5_1_1_0 || p1_1_1_0))"
            self.hierarchy.append(level_two)
        elif case == 3: 
            # ------------------------ task 3 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_1_1_0 && <> (p200_1_1_0 && <> p7_1_1_0))"
            self.hierarchy.append(level_one)

            level_two = dict()
            level_two["p100"] = "<> (p2_2_1_0 && <> p4_1_1_0)"
            level_two["p200"] = "<> (p3_2_1_0 && <> (p5_1_1_0 || p1_1_1_0)) && <> p6_1_1_0 && !p6_1_1_0 U p3_2_1_0"
            self.hierarchy.append(level_two)
        elif case == 4: 
            # ------------------------ task 4 -------------------------
            level_one = dict()
            level_one["p0"] = "<> (p100_1_1_0 && <> p7_1_1_0))"
            self.hierarchy.append(level_one)

            level_two = dict()
            level_two["p100"] = "<> (p200_1_1_0 && <> p4_1_1_0)"
            self.hierarchy.append(level_two)
            
            level_three = dict()
            level_three["p200"] = "<> p3_2_1_0"
            self.hierarchy.append(level_three)
        elif case == 5: 
        # ------------------------ task ICL! -------------------------
            # p100 ICL p200 ! 
            level_one = dict()
            level_one["p0"] = "<> p100_1_1_0 && <> p200_1_1_0 && !p200_1_1_0 U p100_1_1_0"
            self.hierarchy.append(level_one)
            
            # p300 I p400 C p500 L 
            # p1 | p2 .
            level_two = dict()
            level_two["p100"] = '<> p300_1_1_0 && <> p400_1_1_0 && <> p500_1_1_0'
            level_two['p200'] = '<> p1_1_1_0 &&  <> p2_1_1_0'
            self.hierarchy.append(level_two)
            
            # p3 _ p4 | p5 _ p6 - p7 | p8 _ p9 ' p10 | p11 _
            level_three = dict()
            level_three['p300'] = '<> (p3_1_1_0 && <> (p4_1_1_0 && <> p5_1_1_0))'
            level_three['p400'] = '<> (p6_1_1_0 && <> (p7_1_1_0 && <> p8_1_1_0))'
            level_three['p500'] = '<> (p9_1_1_0 && <> (p10_1_1_0 && <> p11_1_1_0))'
            self.hierarchy.append(level_three)
            
        return self.hierarchy
    
    def build_hierarchy_graph(self, vis=False):
        """_summary_
        """
        hierarchy_graph = nx.DiGraph(name='hierarchy')
        for level in self.hierarchy:
            for phi in level.keys():
                hierarchy_graph.add_node(phi, label=phi)
        for idx in range(1, len(self.hierarchy)):
            cur_level = self.hierarchy[idx]
            high_level = self.hierarchy[idx - 1]
            for high_phi, spec in high_level.items():
                for cur_phi in cur_level.keys():
                    if cur_phi in spec:
                        hierarchy_graph.add_edge(high_phi, cur_phi)
        
        # each spec should only appear in one spec at higher level
        for node in hierarchy_graph.nodes():
            if hierarchy_graph.in_degree(node) > 1:
                raise ValueError(f"The in-degree of node {node} is larger than 1")
        # non-leaf node should only contain composite spec    
        for level in self.hierarchy:
            for phi, spec in level.items():
                if hierarchy_graph.out_degree(phi) == 0:
                    continue
                child_phi = hierarchy_graph.succ[phi]
                for child_phi in hierarchy_graph.succ[phi]:
                    spec = spec.replace(child_phi, '')
                if 'p' in spec:
                    raise ValueError(f"{phi} contains primitive spec {spec}")
        
        if vis:
            vis_graph(hierarchy_graph, 'data/spec_hierarchy', latex=False)
            
        return hierarchy_graph
    
        