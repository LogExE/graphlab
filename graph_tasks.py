
from graph import Graph, GraphException

# All tasks should accept graph as first argument!


def task1(gr, v):
    """list vertices with outcome degree larger than given vertex has"""
    if not gr.is_directed():
        raise GraphException("This task requires a directed graph!")

    out_deg = len(gr.get_adjacent(v))
    ret = set()
    for vert in gr.get_vertices():
        if len(gr.get_adjacent(vert)) > out_deg:
            ret.add(vert)
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
    for v_from in newgr.get_vertices():
        for v_to in gr.get_adjacent(v_from):
            if not gr.exists_edge(v_to, v_from):
                newgr.remove_edge(v_from, v_to)

    return newgr


def task4(gr):
    """check whether orgraph is either a forest or a tree"""
    if not gr.is_directed():
        raise GraphException("This task requires a directed graph!")

    degs = [gr.get_incdeg(vert) for vert in gr.get_vertices()]

    if any(deg > 1 for deg in degs):
        return "neither"

    def dfs(v):
        stack = [v]
        used = {v}
        active = set()
        while len(stack) > 0:
            top = stack[-1]
            active.add(top)
            ex = False
            for x in gr.get_adjacent(top):
                if x not in used:
                    stack.append(x)
                    used.add(x)
                    ex = True
                elif x in active:
                    return True
            if not ex:  # need to go back
                stack.pop()
                active.remove(top)
        return False

    if any(dfs(x) for x in gr.get_vertices()):  # cylces
        return "neither"

    if degs.count(0) != 1:
        return "forest"

    return "tree"


def task5(gr, u, v):
    """find vertex such has paths from u and v with the same size"""

    if u == v:
        raise GraphException("Vertices were the same!")

    q = [u, v]
    used = {u, v}
    while len(q) > 0:
        el = q.pop(0)
        for nei in gr.get_adjacent(el):
            if nei not in used:
                q.append(nei)
                used.add(nei)

    return used


def task6(gr):
    """Prim algorithm"""

    if gr.is_directed() or not gr.is_weighted():
        raise GraphException(("This task requires "
                              "a non-directed weighted graph!"))
    
    verts = gr.get_vertices()
    first, *rest = verts

    q = [first]
    used = {first}
    while len(q) > 0:
        el = q.pop(0)
        for nei in gr.get_adjacent(el):
            if nei not in used:
                q.append(nei)
                used.add(nei)

    if used != verts:
        raise GraphException("Graph was not connected!")

    seen = {first}
    res = Graph()
    
    while len(seen) != len(verts):
        medg = None
        for v_from in verts - seen:
            for v_to, w in gr.get_adjacent(v_from).items():
                if v_to in seen:
                    edg = (w, v_from, v_to)
                    if medg is None or edg < medg:
                        medg = edg
        w, v_from, v_to = medg
        seen.add(v_from)
        res.add_edge(v_from, v_to, w)

    return res
