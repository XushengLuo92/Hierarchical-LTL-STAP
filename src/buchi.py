import os
import subprocess
import re
from sympy.logic.boolalg import to_dnf
import networkx as nx

class Buchi(object):
    """_summary_

    Args:
        object (_type_): _description_
    """
    def __init__(self) -> None:
        pass
    
    def construct_buchi_graph(self, formula):
        """
        parse the output of the program ltl2ba and build the buchi automaton
        """
        buchi_graph = nx.DiGraph(name="buchi graph")

        # directory of the program ltl2ba
        dirname = os.path.dirname(__file__)
        # output of the program ltl2ba
        output = subprocess.check_output(dirname + "/./../ltl2ba -f \"" + formula + "\"", shell=True).decode(
            "utf-8")
        # find all states/nodes in the buchi automaton
        state_re = re.compile(r'\n(\w+):\n\t')
        state_group = re.findall(state_re, output)
        # find initial and accepting states
        init = [s for s in state_group if 'init' in s]
        # treat the node accept_init as init node
        accept = [s for s in state_group if 'accept' in s]
        # finish the inilization of the graph of the buchi automaton
        buchi_graph.graph['init'] = init
        buchi_graph.graph['accept'] = accept
        # print("state %d, edge %d" % (len(state_group), output.count("::")))
        # for each state/node, find it transition relations
        for state in state_group:
            # add node
            buchi_graph.add_node(state, label=to_dnf('0'))
            # loop over all transitions starting from current state
            state_if_fi = re.findall(state + r':\n\tif(.*?)fi', output, re.DOTALL)
            if state_if_fi:
                relation_group = re.findall(r':: (\(.*?\)) -> goto (\w+)\n\t', state_if_fi[0])
                for symbol, next_state in relation_group:
                    symbol = symbol.replace('||', '|').replace('&&', '&').replace('!', '~')
                    formula = to_dnf(symbol)
                    # @TODO prune
                    # update node, do not create edges for selfloop
                    if state == next_state:
                        buchi_graph.nodes[state]['label'] = formula
                    else:
                        buchi_graph.add_edge(state, next_state, label=formula)
                        # print(buchi_graph.edges[(state, next_state)])

            else:
                state_skip = re.findall(state + r':\n\tskip\n', output, re.DOTALL)
                if state_skip:
                    buchi_graph.nodes[state]['label'] = to_dnf('1')
                    
        return buchi_graph