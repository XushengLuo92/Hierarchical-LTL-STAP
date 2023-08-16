import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from specification import Specification
from buchi import BuchiConstructor
from util import create_parser, vis_graph

from collections import namedtuple
Hierarchy = namedtuple('Hierarchy', ['level', 'phi', 'buchi_graph', 'decomp_sets'])

def main(args=None):
    parser = create_parser()
    args = parser.parse_known_args()[0]

    specs = Specification()
    specs.get_task_specification(task=args.task, case=args.case)
    hierarchy_graph = specs.build_hierarchy_graph(args.vis)
    print(specs.hierarchy)
    
    buchi_constructor = BuchiConstructor()
    task_hierarchy = dict()
    for index, level in enumerate(specs.hierarchy):
        for (phi, spec) in level.items():
            buchi_graph = buchi_constructor.construct_buchi_graph(spec)
            decomp_sets = None
            if hierarchy_graph.out_degree(phi) == 0:
                decomp_sets = buchi_constructor.get_all_decomp_nodes(buchi_graph=buchi_graph)
            task_hierarchy[phi] = Hierarchy(level=index+1, phi=phi, buchi_graph=buchi_graph, decomp_sets=decomp_sets)
    # print(task_hierarchy.items())
    if args.vis:
        for task, h in task_hierarchy.items():
            vis_graph(h.buchi_graph, f'data/{task}', latex=False)
            
if __builtins__:
    main()