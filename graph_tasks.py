
from graph import Graph, GraphException

def task1(gr, vertex):
    """list vertices with outcome degree larger than given vertex has"""
    if not gr.is_directed():
        raise GraphException("This task requires a directed graph!")
    
    od = len(gr.get_adjacent(vertex))
    ret = set()
    for u in gr.get_vertices():
        if len(gr.get_adjacent(u)) > od:
            ret.add(u)
    return ret

def task2(gr, vertex):
    """list non-adjacent vertices for given vertex"""
    if gr.is_directed():
        raise GraphException("This task requires a non-directed graph!")

    return gr.get_vertices() - gr.get_adjacent(vertex).keys() - {vertex}

def task3(gr):
    """delete solo edges from directed graph"""
    if not gr.is_directed():
        raise GraphException("This task requires a directed graph!")

    newgr = Graph(gr)
    
    conf = newgr.get_full()
    for v in conf:
        for u in conf[v]:
            if v not in conf[u]:
                newgr.remove_edge(v, u)

    return newgr
