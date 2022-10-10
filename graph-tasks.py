
from graph import GraphException

def task1(gr, v):
    ('Get vertices '
     'with outcome degree larger '
     'than given vertex has')
    if not gr.is_directed():
        raise GraphException("This task requires a directed graph!")
    
    od = len(gr.get_adjacent(v))
    ret = set()
    for u in gr.get_vertices():
        if len(gr.get_adjacent(u)) > od:
            ret.add(u)
    return ret
