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
        if case == 12:
            # case 1 in IJRR STAP and TRO
            level_one = dict()
            level_one["p0"] = '<> p100 && <> p200'
            self.hierarchy.append(level_one)
            level_two = dict()
            level_two["p100"] = "<> (d5 && default && X ((carrybin U dispose) && <> default)) && [](carrybin -> !publicc)"
            level_two["p200"] = "<> (d5 && emptybin && X (d5 && default))"
            self.hierarchy.append(level_two)
            
        elif case == 13:
            # case 3 in IJRR STAP and case 2 in TRO
            level_one = dict()
            level_one["p0"] = '<> p100 && <> p200 && <> p300'
            self.hierarchy.append(level_one)
            level_two = dict()
            level_two["p100"] = "<> (p && carry U (d10 && X !carry)) && [] (carry -> !publicc)"
            level_two["p200"] = "<> (p && carry U (d7 && X !carry)) && [] (carry -> !publicc)"
            level_two["p300"] = "<> (p && carry U (d5 && X !carry)) && [] (carry -> !publicc)"
            self.hierarchy.append(level_two)
            
        elif case == 14:
            # case 4 in IJRR STAP and case 3 in TRO
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
            # case 1 in AI2THOR
            level_one = dict()
            level_one["p0"] = "<> p100"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p100'] = "<> (apple37512a22 && carry000apple37512a22) && <> (cabinet19b27166 && camera000cabinet19b27166)"
            self.hierarchy.append(level_two)

        elif case == 24:
            level_one = dict()
            level_one["p0"] = "<> p100 && <> p200"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p100'] = "<> d3 && ! d5 U d3"
            level_two['p200'] = "<> d5 && ! d3 U d5"
            self.hierarchy.append(level_two)
            
        elif case == 25:
            level_one = dict()
            level_one["p0"] = "<> ( p101 && ( <> ( p102 && <> p103 ) ) ) "
            # level_one["p0"] = "<>  p101 &&  <>  p102 && <> p103 "
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p101'] = "<> ( p104 ) && ( <> p105 )"
            level_two['p102'] = "<> p106"
            level_two['p103'] = "<> p107"
            self.hierarchy.append(level_two)
            
            level_three = dict()
            level_three['p104'] = "<> d2"
            level_three['p105'] = "<> d3"
            level_three['p106'] = "<> m5"
            level_three['p107'] = "<> d10"
            self.hierarchy.append(level_three)
        
        elif case == 26:
            level_one = dict()
            # level_one["p0"] = "<> ( p101 &&  <>  p102 ) "
            level_one["p0"] = "<>  p101 &&  <>  p102"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p101'] = "<> d2 && <> d3"
            level_two['p102'] = "<> m5"
            self.hierarchy.append(level_two)
            
        elif case == 27:
            level_one = dict()
            level_one["p0"] = "<> ( p101 && ( <> ( p102 && ( <> p103 && <> p104 ) ) ) ) )"
            # level_one["p0"] = "<>  p101 &&  <>  p102"
            self.hierarchy.append(level_one)
            
            level_two = dict()
            level_two['p101'] = "<> ( d3 && ( <> m5 ) )"
            level_two['p102'] = "<> d10"
            level_two['p103'] = "( <> d2 ) && ( <> d1 )"
            level_two['p104'] = "<> ( d14 && ( <> g ) )"
            self.hierarchy.append(level_two)
           
            # level_three = dict()
            # level_three['p105'] = "<> d3"
            # level_three['p106'] = "<> m5"
            # level_three['p107'] = "<> d10"
            # level_three['p108'] = "<> d2"
            # level_three['p109'] = "<> d1"
            # level_three['p110'] = "<> d14"
            # level_three['p111'] = "<> g"
            # self.hierarchy.append(level_three)

        return self.hierarchy
    
    def get_manipulation_specification(self, case):
        """_summary_

        Args:
            case (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.hierarchy = []
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
    
        