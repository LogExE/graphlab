
from graph import Graph, GraphException

# Task should accept graph as first argument!

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

    verts = newgr.get_vertices()
    for v in verts:
        for u in verts:
            if gr.exists_edge(v, u) and not gr.exists_edge(u, v):
                newgr.remove_edge(v, u)

    return newgr
