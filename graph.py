
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

    def __set_attribs(self, attribs):
        if len(self.__attributes) != 0:
            raise GraphException("Tried to override attributes!")
        if len(attribs) != 2:
            raise GraphFormatException(("Number of graph attributes "
                                        "were other than 2!"))

        if attribs[0] not in Graph.attrib_list or \
           attribs[1] not in Graph.attrib_list:
            raise GraphFormatException(("One of attributes "
                                        "can't be recognized!"))

        if attribs[0] == attribs[1]:
            raise GraphFormatException("Attributes were the same!")

        self.__attributes = set(attribs)

    def load(self, name):
        with open(name) as f:
            self.__set_attribs(f.readline().split())
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

    def __init__(self, arg=None):
        self.__vertices = {}
        self.__attributes = set()
        if arg is None:
            self.__attributes = {"weighted", "directed"}
        elif isinstance(arg, str):
            self.load(arg)
        elif isinstance(arg, Graph):
            self.__attributes = copy.deepcopy(arg.__attributes)
            self.__vertices = copy.deepcopy(arg.__vertices)
        elif isinstance(arg, Iterable):
            self.__set_attribs(arg)
        else:
            raise GraphException(("Constructor accepts either "
                                  "nothing (None), path to file "
                                  ", another graph or "
                                  "iterable with attributes!"))

    def is_weighted(self):
        return "weighted" in self.__attributes

    def is_directed(self):
        return "directed" in self.__attributes

    def get_vertices(self):
        return self.__vertices.keys()
        
    def get_adjacent(self, v):
        if v not in self.__vertices:
            raise GraphException("No such vertex!")

        return copy.deepcopy(self.__vertices[v])

    def add_vertex(self, x):
        if x in self.__vertices:
            raise GraphOperationException("Tried to add existing vertex!")
        
        self.__vertices[x] = {}
            
    def remove_vertex(self, x):
        if x not in self.__vertices:
            raise GraphOperationException(
                "Tried to delete nonexistant vertex!")

        for v in self.__vertices:
            if v != x and x in self.__vertices[v]:
                self.remove_edge(v, x)
        del self.__vertices[x]

    def add_edge(self, x, y, price=None):
        if price is None and "weighted" in self.__attributes or \
           price is not None and "not_weighted" in self.__attributes:
            raise GraphOperationException(("Tried to insert edge "
                                           f"with price {price}, "
                                           "which is unallowed!"))
        if x not in self.__vertices:
            self.add_vertex(x)
        if y not in self.__vertices:
            self.add_vertex(y)
            
        if y in self.__vertices[x]:
            raise GraphOperationException("Tried to add an existing edge!")
        
        self.__vertices[x][y] = price
        if "not_directed" in self.__attributes:
            self.__vertices[y][x] = price

    def remove_edge(self, x, y):
        if x not in self.__vertices or y not in self.__vertices[x]:
            raise GraphException("Tried to remove nonexistant edge!")
        
        del self.__vertices[x][y]
        if "not_directed" in self.__attributes:
            del self.__vertices[y][x]
            

    def save(self, path):
        isolated = set(self.__vertices.keys())
        buff = []
        appended = set()
        for v in self.__vertices:
            for u in self.__vertices[v]:
                if "not_weighted" in self.__attributes and (u, v) in appended:
                    continue
                isolated.discard(v)
                isolated.discard(u)
                price = self.__vertices[v][u]
                if price is None:
                    buff.append(f"{v} {u}")
                else:
                    buff.append(f"{v} {u} {price}")
                appended.add((v, u))
        with open(path, 'w') as f:
            f.write(" ".join(self.__attributes) + "\n")
            f.write("\n".join(isolated) + "\n")
            f.write("\n".join(buff) + "\n")
