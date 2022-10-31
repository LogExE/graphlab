
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
    
    def dfs(x):
        stack = [x]
        used = {x}
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
                    return None
            if not ex: # need to go back
                stack.pop()
                active.remove(top)
        return used

    res = {x: dfs(x) for x in gr.get_vertices()}
    if any(x is None for x in res): # FOUND CYCLE!!!
        return "neither"
    
    for k in res.keys():
        if len([x for x in res if k in x]) != 0:
            del res[k]

    return res


def task5(gr, u, v):
    """find vertex such has paths from u and v with the same size"""
    
    q = [u, v]
    froms = {u: 0, v: 1}
    lens = {u: 0, v: 0}
    sus = set()
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
                    sus.add(nei)

    ans = set()
    for s in sus:
        ans = ans.union(gr.get_adjacent(s))
        ans.add(s)

    return ans

def task6(gr):
    """Prim"""
    
    if gr.is_directed() or not gr.is_weighted():
        raise GraphException(("This task requires "
                              "a non-directed weighted graph!"))

    
