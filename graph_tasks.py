
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


def task5(gr, u, v):  # TODO: solve this one
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
    first, *_ = verts

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
        if medg is None:
            raise GraphException("Graph was not connected!")
        w, v_from, v_to = medg
        seen.add(v_from)
        res.add_edge(v_from, v_to, w)

    return res


INF = 10 ** 9


def task7(gr, u):
    """counts of shortest paths from u to other vertices"""

    if not gr.is_weighted():
        raise GraphException("This task requires a weighted graph!")

    verts = gr.get_vertices()
    d = {v: INF for v in verts}
    d[u] = 0
    pred = {v: set() for v in verts}

    unused = set(verts)
    cur = u
    while len(unused) > 0:
        for y, w in gr.get_adjacent(cur).items():
            try:
                w = float(w)
            except ValueError:
                raise GraphException(("Graph has a "
                                      "non-numeric edge mark!"))
            if w < 0:
                raise GraphException("Graph has a negative edge!")
            if d[y] > d[cur] + w:
                pred[y] = {cur}
                d[y] = d[cur] + w
            elif d[y] == d[cur] + w:
                pred[y].add(cur)
        unused.remove(cur)
        cur = min(unused, default=None, key=lambda x: d[x])

    ways = {v: 0 for v in verts}
    ways[u] = 1

    def calc(x):
        for y in gr.get_adjacent(x):
            if x in pred[y]:
                ways[y] += ways[x]
                pred[y].remove(x)
                if len(pred[y]) == 0:
                    calc(y)

    calc(u)

    return ways


def task8(gr, u, v, k):  # TODO: find k shortest in sorted order instead
    """find k shortest paths from u to v"""

    if not gr.is_weighted():
        raise GraphException("This task requires a weighted graph!")

    verts = gr.get_vertices()
    d = {v: INF for v in verts}
    d[u] = 0
    pred = {v: set() for v in verts}
    k = int(k)

    for _ in range(len(verts) - 1):
        for x in verts:
            for y, w in gr.get_adjacent(x).items():
                try:
                    w = float(w)
                except ValueError:
                    raise GraphException(("Graph has a "
                                          "non-numeric edge mark!"))
                if d[y] > d[x] + w:
                    pred[y] = {x}
                    d[y] = d[x] + w
                elif d[y] == d[x] + w:
                    pred[y].add(x)

    for x in verts:
        for y, w in gr.get_adjacent(x).items():
            if d[y] > d[x] + int(w):
                raise GraphException("Graph has a negative cycle!")

    ways = []

    def calc(cur, path):
        mod_path = cur + (" " + path if path != "" else "")
        if len(pred[cur]) == 0:
            ways.append(mod_path)
            return

        for prev in pred[cur]:
            calc(prev, mod_path)

    calc(v, "")

    return ways[:k]


def task9(gr):  # TODO: consider negative cycles
    """find shortest path from each pair of vertices"""
    if not gr.is_weighted():
        raise GraphException("This task requires a weighted graph!")

    verts = gr.get_vertices()

    d = {v: {} for v in verts}
    nxt = {v: {} for v in verts}
    for v in verts:
        adj = gr.get_adjacent(v)
        for u in adj:
            try:
                d[v][u] = float(adj[u])
            except ValueError:
                raise GraphException(("Graph has a "
                                      "non-numeric edge mark!"))
            nxt[v][u] = u
        for u in verts - adj.keys():
            d[v][u] = INF
            nxt[v][u] = None
        d[v][v] = 0
        nxt[v][v] = v

    for x in verts:
        for y in verts:
            for z in verts:
                if d[y][x] + d[x][z] < d[y][z]:
                    d[y][z] = d[y][x] + d[x][z]
                    nxt[y][z] = nxt[y][x]

    ways = {v: {} for v in verts}
    for v in verts:
        for u in verts:
            if nxt[v][u] is None:
                continue
            nodes = []
            c = v
            while c != u:
                nodes.append(c)
                c = nxt[c][u]
            nodes.append(u)
            ways[v][u] = " ".join(nodes)

    return ways
