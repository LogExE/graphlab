
import heapq
from graph import Graph, GraphException

# All tasks should accept graph as first argument!

def task1(gr, v):
    """list vertices with outcome degree larger than given vertex has"""
    if not gr.is_directed():
        raise GraphException("This task requires a directed graph!")
    
    od = len(gr.get_adjacent(v))
    ret = set()
    for u in gr.get_vertices():
        if len(gr.get_adjacent(u)) > od:
            ret.add(u)
    return ret

def task2(gr, v):
    """list non-adjacent vertices for given vertex"""
    if gr.is_directed():
        raise GraphException("This task requires a non-directed graph!")

    return gr.get_vertices() - gr.get_adjacent(v).keys() - {v}

def task3(gr):
    """delete solo edges from directed graph"""
    if not gr.is_directed():
        raise GraphException("This task requires a directed graph!")

    newgr = Graph(gr)
    for v in newgr.get_vertices():
        for u in gr.get_adjacent(v):
            if not gr.exists_edge(u, v):
                newgr.remove_edge(v, u)

    return newgr

def task4(gr):
    """check whether orgraph is either a forest or a tree"""
    if not gr.is_directed():
        raise GraphException("This task requires a directed graph!")

    ans = None
    
    def dfs(x):
        nonlocal ans
        st[x] = 1
        for u in gr.get_adjacent(x):
            if st.get(u, 0) == 0:
                dfs(u)
            elif st[u] == 1:
                ans = ans or "neither"
        st[x] = 2
    
    for v in gr.get_vertices():
        st = {}
        dfs(v)
        if st.keys() == gr.get_vertices():
            ans = ans or "tree"
    ans = ans or "forest"

    # TODO: income degree

    return ans

def task5(gr, u, v):
    """find vertex such has paths from u and v with the same size"""
    
    q = [u, v]
    froms = {u: 0, v: 1}
    lens = {u: 0, v: 0}
    ans = set()
    while len(q) > 0:
        el = q.pop(0)
        for nei in gr.get_adjacent(el):
            if nei not in lens:
                lens[nei] = lens[el] + 1
                froms[nei] = froms[el]
                q.append(nei)
            elif froms[nei] != froms[el]:
                froms[nei] = 2
                if lens[el] + 1 == lens[nei]:
                    ans.add(nei)

    return ans
