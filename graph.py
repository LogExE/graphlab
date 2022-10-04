
from collections.abc import Iterable
import copy

class GraphException(Exception):
    pass

class GraphFormatException(GraphException):
    pass

class GraphOperationException(GraphException):
    pass

class Graph():
    attrib_list = ("weighted", "not_weighted",
                   "directed", "not_directed")

    def set_attribs(self, attribs):
        if len(attribs) != 2:
            raise GraphFormatException(("Number of graph attributes "
                                            "were other than 2!"))
            
        if attribs[0] not in Graph.attrib_list or \
           attribs[1] not in Graph.attrib_list:
            raise GraphFormatException(("One of attributes "
                                    "can't be recognized!"))
                
        if attribs[0] == attribs[1]:
            raise GraphFormatException("Attributes were the same!")
            
        self.attributes = set(attribs)

    
    def load(self, name):
        with open(name) as f:
            self.set_attribs(f.readline().split())
            for i, line in enumerate(f, 2):
                a = line.split()
                if len(a) == 0:
                    continue
                if len(a) == 1:
                    self.add_vertex(a[0])
                elif len(a) in [2, 3]:
                    self.add_edge(*a)
                else:
                    raise GraphFormatException(("Format of line "
                                                f"{i} is incorrect!"))
    
    def __init__(self, arg = None):
        self.vertices = {}
        if arg is None:
            self.attributes = {"weighted", "directed"}
        elif isinstance(arg, str):
            self.load(arg)
        elif isinstance(arg, Graph):
            self.attributes = arg.attributes
            self.vertices = copy.deepcopy(arg.vertices)
        elif isinstance(arg, Iterable):
            self.set_attribs(arg)
        else:
            raise GraphException(("Constructor accepts either "
                                  "nothing (None), path to file "
                                  "or another graph!"))

    def add_vertex(self, x):
        if x not in self.vertices:
             self.vertices[x] = {}
        else:
            raise GraphOperationException("Tried to add existing vertex!")

    def remove_vertex(self, x):
        if x in self.vertices:
            del self.vertices[x]
            for v in self.vertices:
                if v != x and x in self.vertices[v]:
                    self.remove_edge(v, x)
        else:
            raise GraphOperationException("Tried to delete nonexistant vertex!")        
            
    def add_edge(self, x, y, price = None):
        if price is None and "weighted" in self.attributes or \
           price is not None and "not_weighted" in self.attributes:
            raise GraphOperationException(("Tried to insert edge "
                                           f"with price {price}, "
                                           "which is unallowed!"))
        if x not in self.vertices:
            self.add_vertex(x)
        if y not in self.vertices:
            self.add_vertex(y)

        if y not in self.vertices[x]:
            self.vertices[x][y] = price
            if "not_directed" in self.attributes:
                self.vertices[y][x] = price
        else:
            raise GraphOperationException("Tried to add an existing edge!")

    def remove_edge(self, x, y):
        if x in self.vertices:
            if y in self.vertices[x]:
                del self.vertices[x][y]
                if "not_directed" in self.attributes:
                    del self.vertices[y][x]
        else:
            raise GraphException("Tried to remove nonexistant edge!")
    
    def save(self, path):
        isolated = set(self.vertices.keys())
        buff = []
        appended = set()
        for v in self.vertices:
            for u in self.vertices[v]:
                if "not_weighted" in self.attributes and (u, v) in appended:
                    continue
                isolated.discard(v)
                isolated.discard(u)
                price = self.vertices[v][u]
                if price is None:
                    buff.append(f"{v} {u}")
                else:
                    buff.append(f"{v} {u} {price}")
                appended.add((v, u))
        with open(path, 'w') as f:
            f.write(" ".join(self.attributes) + "\n")
            f.write("\n".join(isolated) + "\n")
            f.write("\n".join(buff) + "\n")
