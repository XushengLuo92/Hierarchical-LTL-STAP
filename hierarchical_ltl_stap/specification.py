import networkx as nx 
from .util import vis_graph

task1 = "<> (d5 && default && X ((carrybin U dispose) && <> default)) && [](carrybin -> !publicc)  && \
            <> (d5 && emptybin && X (d5 && default))"
task2 = "<> (p && carry U (d10 && X !carry)) && \
            <> (p && carry U (d7 && X !carry)) && \
            <> (p && carry U (d5 && X !carry)) && [] (carry -> !publicc)"
task3 = "<> (d5 && carry U (d3 && X !carry)) && [] (carry -> !publicc) && \
            <> (d11 && guide U (m6 && X !guide)) && \
            <> (m1 && photo) && \
            <> (m4 && photo) && \
            <> (m6 && photo) && \
            [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
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
            # level_one["p0"] = '<> p100 && <> p200 && <> p300'
            level_one["p0"] = '<> p100 && <> p200'
            self.hierarchy.append(level_one)
            level_two = dict()
            # level_two['p100'] = '<> p1 && [](c -> X<> p5) && [](d -> X<> p3)'
            level_two['p100'] = '<> p2 && <> p5'
            level_two['p200'] = '<> p3 && <> p4'
            # level_two['p300'] = '<> p1 && <> p6'
            self.hierarchy.append(level_two)
        elif case == 10:
            level_one = dict()
            level_one["p0"] = '<> p200'
            # level_one["p0"] = '<> p100 && <> p300 && <> p200'
            self.hierarchy.append(level_one)
            level_two = dict()
            # level_two["p100"] = '<> p1 && [] (injury -> X help)' 
            level_two['p200'] = '<> p6 && [] (damage -> <> photo)'
            # level_two['p300'] = '<> p2 && <> p5 && <> p3'
            # level_two['p300'] = '<> p3'
            # level_two['p200'] = '<> (p6 && X(photo U p4))'
            # level_two["p200"] = '<> p5 && <> p6 && !p6 U p5'
            self.hierarchy.append(level_two)
        elif case == 11:
            level_one = dict()
            level_one["p0"] = '!p200 U p100'
            # level_one["p0"] = '<> p100 && <> p300 && <> p200'
            self.hierarchy.append(level_one)
            level_two = dict()
            level_two["p100"] = '<> p4' 
            level_two['p200'] = '<> p3'
            self.hierarchy.append(level_two)
        
        elif case == 12:
            # case 1 in IJRR STAP and RSS 
            level_one = dict()
            level_one["p0"] = '<> p100 && <> p200'
            self.hierarchy.append(level_one)
            level_two = dict()
            level_two["p100"] = "<> (d5 && default && X ((carrybin U dispose) && <> default)) && [](carrybin -> !publicc)"
            level_two["p200"] = "<> (d5 && emptybin && X (d5 && default))"
            self.hierarchy.append(level_two)
            
        elif case == 13:
            # case 3 in IJRR STAP and case 2 in RSS
            level_one = dict()
            level_one["p0"] = '<> p100 && <> p200 && <> p300'
            self.hierarchy.append(level_one)
            level_two = dict()
            level_two["p100"] = "<> (p && carry U (d10 && X !carry)) && [] (carry -> !publicc)"
            level_two["p200"] = "<> (p && carry U (d7 && X !carry)) && [] (carry -> !publicc)"
            level_two["p300"] = "<> (p && carry U (d5 && X !carry)) && [] (carry -> !publicc)"
            self.hierarchy.append(level_two)
            
        elif case == 14:
            # deeper version of case 4 in IJRR STAP
            level_one = dict()
            level_one["p0"] = "<> p100 && <> p200 && <> p300"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p100'] = "<> p101 && <> p102 && <> p103"
            level_two['p200'] = "<> (d5 && carry U (d3 && X !carry)) && [] (carry -> !publicc)"
            level_two['p300'] = "<>(d11 && guide U (m6 && X !guide))"
            self.hierarchy.append(level_two)
            
            level_three = dict()
            # level_three["p101"] = "<> p3"
            level_three["p101"] = "<> (m1 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            level_three["p102"] = "<> (m4 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            level_three["p103"] = "<> (m6 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            self.hierarchy.append(level_three)
        
        elif case == 15:
            # flat version of case 1 in IJRR STAP
            level_one = dict()
            level_one["p0"] = "<> p100"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p100'] = \
              "<> (d5 && default && X ((carrybin U dispose) && <> default)) && [](carrybin -> !publicc)  && \
               <> (d5 && emptybin && X (d5 && default))"
            self.hierarchy.append(level_two)
            
        elif case == 16:
            # flat version of case 2 in IJRR STAP
            level_one = dict()
            level_one["p0"] = "<> p100"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p100'] = \
            "<> (p && carry U (d10 && X !carry)) && \
             <> (p && carry U (d7 && X !carry)) && \
             <> (p && carry U (d5 && X !carry)) && [] (carry -> !publicc)"
            self.hierarchy.append(level_two)
            
        elif case == 17:
            # flat version of case 4 in IJRR STAP
            # less runtime but larger cost
            level_one = dict()
            level_one["p0"] = "<> p100"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p100'] = \
               "<> (d5 && carry U (d3 && X !carry)) && [] (carry -> !publicc) && \
                <> (d11 && guide U (m6 && X !guide)) && \
                <> (m1 && photo) && \
                <> (m4 && photo) && \
                <> (m6 && photo) && \
                [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            self.hierarchy.append(level_two)
        
        elif case == 18:
            # hierarchical version of combined task 1 and 2
            level_one = dict()
            level_one["p0"] = '<> p100 && <> p200'
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two["p100"] = '<> p101 && <> p102'
            level_two["p200"] = '<> p201 && <> p202 && <> p203'
            self.hierarchy.append(level_two)
            
            level_three = dict()
            level_three["p101"] = "<> (d5 && default && X ((carrybin U dispose) && <> default)) && [](carrybin -> !publicc)"
            level_three["p102"] = "<> (d5 && emptybin && X (d5 && default))"
            level_three["p201"] = "<> (p && carry U (d10 && X !carry)) && [] (carry -> !publicc)"
            level_three["p202"] = "<> (p && carry U (d7 && X !carry)) && [] (carry -> !publicc)"
            level_three["p203"] = "<> (p && carry U (d5 && X !carry)) && [] (carry -> !publicc)"
            self.hierarchy.append(level_three)
        
        elif case == 19:
            # hierarchical version of combined task 1 and 3
            level_one = dict()
            level_one["p0"] = '<> p100 && <> p200'
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two["p100"] = '<> p101 && <> p102'
            level_two["p200"] = '<> p201 && <> p202 && <> p203'
            self.hierarchy.append(level_two)
            
            level_three = dict()
            level_three["p101"] = "<> (d5 && default && X ((carrybin U dispose) && <> default)) && [](carrybin -> !publicc)"
            level_three["p102"] = "<> (d5 && emptybin && X (d5 && default))"
            level_three['p201'] = "<> p301 && <> p302 && <> p303"
            level_three['p202'] = "<> (d5 && carry U (d3 && X !carry)) && [] (carry -> !publicc)"
            level_three['p203'] = "<> (d11 && guide U (m6 && X !guide))"
            self.hierarchy.append(level_three)
            
            level_four = dict()
            level_four["p301"] = "<> (m1 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            level_four["p302"] = "<> (m4 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            level_four["p303"] = "<> (m6 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            self.hierarchy.append(level_four)
            
        elif case == 20:
            # hierarchical version of combined task 2 and 3
            level_one = dict()
            level_one["p0"] = '<> p100 && <> p200'
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two["p100"] = '<> p101 && <> p102 && <> p103'
            level_two["p200"] = '<> p201 && <> p202 && <> p203'
            self.hierarchy.append(level_two)
            
            level_three = dict()
            level_three["p101"] = "<> (p && carry U (d10 && X !carry)) && [] (carry -> !publicc)"
            level_three["p102"] = "<> (p && carry U (d7 && X !carry)) && [] (carry -> !publicc)"
            level_three["p103"] = "<> (p && carry U (d5 && X !carry)) && [] (carry -> !publicc)"
            level_three['p201'] = "<> p301 && <> p302 && <> p303"
            level_three['p202'] = "<> (d5 && carry U (d3 && X !carry)) && [] (carry -> !publicc)"
            level_three['p203'] = "<> (d11 && guide U (m6 && X !guide))"
            self.hierarchy.append(level_three)
            
            level_four = dict()
            level_four["p301"] = "<> (m1 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            level_four["p302"] = "<> (m4 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            level_four["p303"] = "<> (m6 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            self.hierarchy.append(level_four)
        
        elif case == 21:
            # hierarchical version of combined task 1 and 2 and 3
            level_one = dict()
            level_one["p0"] = '<> p100 && <> p200 && <> p300'
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two["p100"] = '<> p101 && <> p102'
            level_two["p200"] = '<> p201 && <> p202 && <> p203'
            level_two["p300"] = '<> p301 && <> p302 && <> p303'
            self.hierarchy.append(level_two)
            
            level_three = dict()
            level_three["p101"] = "<> (d5 && default && X ((carrybin U dispose) && <> default)) && [](carrybin -> !publicc)"
            level_three["p102"] = "<> (d5 && emptybin && X (d5 && default))"
            level_three["p201"] = "<> (p && carry U (d10 && X !carry)) && [] (carry -> !publicc)"
            level_three["p202"] = "<> (p && carry U (d7 && X !carry)) && [] (carry -> !publicc)"
            level_three["p203"] = "<> (p && carry U (d5 && X !carry)) && [] (carry -> !publicc)"
            level_three['p301'] = "<> p401 && <> p402 && <> p403"
            level_three['p302'] = "<> (d5 && carry U (d3 && X !carry)) && [] (carry -> !publicc)"
            level_three['p303'] = "<> (d11 && guide U (m6 && X !guide))"
            self.hierarchy.append(level_three)
            
            level_four = dict()
            level_four["p401"] = "<> (m1 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            level_four["p402"] = "<> (m4 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            level_four["p403"] = "<> (m6 && photo) && [] (!(m1 || m2 || m3 || m4 || m5 || m6) -> !camera)"
            self.hierarchy.append(level_four)
        
        elif case == 22:
            # flat version of combined task
            level_one = dict()
            level_one["p0"] = "<> p100"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            # level_two['p100'] = task1 + ' && ' + task2
            level_two['p100'] = "<> (d5 && default && X ((carrybin U dispose) && <> default)) && [](carrybin -> !publicc)  && \
            <> (d5 && emptybin && X (d5 && default)) && \
            <> (p && carry U (d10 && X !carry)) && \
            <> (p && carry U (d7 && X !carry)) && \
            <> (p && carry U (d5 && X !carry)) && [] (carry -> !publicc)"
            self.hierarchy.append(level_two)
        
        elif case == 23:
            level_one = dict()
            level_one["p0"] = "<> p100"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p100'] = "<> (apple37512a22 && carry && <> (bowl2813285c && camera))"
            self.hierarchy.append(level_two)
        
            
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
    
        