
import copy

class GraphFormatException(Exception):
    pass

class Graph():
    def __init__(self, arg1 = None):
        self.vertices = {}
        self.prices = {}
        if isinstance(arg1, str):
            with open(arg1) as f:
                for line in f:
                    a = line.split()
                    if len(a) == 0:
                        continue
                    if len(a) == 1:
                        self.add_vertex(a[0])
                    elif len(a) == 2:
                        self.add_edge(a[0], a[1])
                    elif len(a) == 3:
                        self.add_edge(a[0], a[1], a[2])
                    else:
                        raise GraphFormatException()
        elif isinstance(arg1, Graph):
            self.vertices = copy.deepcopy(arg1.vertices)
            self.prices = copy.deepcopy(arg1.prices)

    def add_vertex(self, x):
        if x not in self.vertices:
             self.vertices[x] = set()
             return True
        return False

    def remove_vertex(self, x):
        if x in self.vertices:
            del self.vertices[x]
            self.prices = {e: p for e, p in self.prices.items() if e[0] != x}
            for v in self.vertices:
                if x in self.vertices[v]:
                    self.remove_edge(v, x)
            return True
        return False
            
    def add_edge(self, x, y, price = None):
        if x not in self.vertices:
            self.add_vertex(x)
        if y not in self.vertices:
            self.add_vertex(y)

        if y not in self.vertices[x]:
            self.vertices[x].add(y)
            self.prices[(x, y)] = price
            return True
        return False

    def remove_edge(self, x, y):
        if x in self.vertices:
            if y in self.vertices[x]:
                self.vertices[x].remove(y)
                del self.prices[(x, y)]
                return True
        return False
    
    def save(self, path):
        with open(path, 'w') as f:
            for v in self.vertices:
                if len(self.vertices[v]) == 0:
                    f.write(f"{v}\n")
                else:
                    for u in self.vertices[v]:
                        price = self.prices.get((v, u))
                        if price is None:
                            f.write(f"{v} {u}\n")
                        else:
                            f.write(f"{v} {u} {price}\n")
