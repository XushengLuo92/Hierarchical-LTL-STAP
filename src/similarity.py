import editdistance
from buchi import BuchiConstructor
import networkx as nx


def get_all_words(spec):
    buchi_constructor = BuchiConstructor()
    buchi_graph = buchi_constructor.construct_buchi_graph(spec)
    buchi_graph.graph['conflict_aps'] = []
    buchi_constructor.prune_graph(buchi_graph)
    buchi_constructor.prune_clauses(buchi_graph)
    all_simple_paths = []
    for init in buchi_graph.graph['init']:
        for accept in buchi_graph.graph['accept']:
            all_simple_paths.extend(nx.algorithms.all_simple_paths(buchi_graph, init, accept))
    
    all_words = []
    for simple_path in all_simple_paths:
        all_words.append([str(buchi_graph.edges[(simple_path[idx], simple_path[idx+1])]['label'])
                          for idx in range(len(simple_path) - 1)])
    return all_words

def calc_similarity_wrt_latter(all_words_a, all_words_b):
    max_similarity = 0
    for word_a in all_words_a:
        min_similarity = 1e3
        for word_b in all_words_b:
            min_similarity = min(min_similarity, editdistance.eval(word_a, word_b))
        max_similarity = max(max_similarity, min_similarity)
    return max_similarity

def main():
    specification_a = '<> b && <> a'
    all_words_a = get_all_words(specification_a)
    
    specification_b = '<> a &&  <> b'
    all_words_b = get_all_words(specification_b)
    
    max_similarity = calc_similarity_wrt_latter(all_words_a, all_words_b)
    max_similarity = max(max_similarity, calc_similarity_wrt_latter(all_words_b, all_words_a))
    print(f"spec {specification_a} and {specification_b}: max similarity {max_similarity}")
    
if __builtins__:
    main()