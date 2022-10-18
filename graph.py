
from collections.abc import Iterable
import copy


class GraphException(Exception):
    pass


class GraphOperationException(GraphException):
    pass


class Graph():
    def __set_attribs(self, attribs):
        if len(self.__attributes) != 0:
            raise GraphException("Tried to override attributes!")
        for atr in attribs:
            if atr in ("weighted", "not_weighted") and \
               "weighted" in self.__attributes or \
               atr in ("directed", "not_directed") and \
               "directed" in self.__attributes:
                raise GraphException("One of attributes repeated!")
            
            if atr == "weighted":
                self.__attributes["weighted"] = True
            elif atr == "not_weighted":
                self.__attributes["weighted"] = False
            elif atr == "directed":
                self.__attributes["directed"] = True
            elif atr == "not_directed":
                self.__attributes["directed"] = False
            else:
                raise GraphException(("One of atttributes "
                                      "wasn't unrecognized: " + atr))

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
                    raise GraphException(("Format of line "
                                          f"{i} is incorrect!"))

    def __init__(self, arg=None):
        self.__vertices = {}
        self.__attributes = {}
        if arg is None:
            self.__set_attribs(("directed", "weighted"))
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
        return self.__attributes["weighted"]

    def is_directed(self):
        return self.__attributes["directed"]

    def exists_edge(self, x, y):
        return x in self.__vertices and y in self.__vertices[x]

    def get_vertices(self):
        return set(self.__vertices.keys())
        
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
        if (price is not None) != (self.is_weighted()):
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
        if not self.is_directed():
            self.__vertices[y][x] = price

    def remove_edge(self, x, y):
        if x not in self.__vertices or y not in self.__vertices[x]:
            raise GraphException("Tried to remove nonexistant edge!")
        
        del self.__vertices[x][y]
        if not self.is_directed():
            del self.__vertices[y][x]

    def __list_attributes(self):
        return set(map(lambda x:("" if x[1] else "not_") + x[0], \
                       self.__attributes.items()))
    
    def save(self, path):
        isolated = set(self.__vertices.keys())
        buff = []
        appended = set()
        for v in self.__vertices:
            for u in self.__vertices[v]:
                if not self.is_directed() and (u, v) in appended:
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
            f.write(" ".join(self.__list_attributes()) + "\n")
            f.write("\n".join(isolated) + "\n")
            f.write("\n".join(buff) + "\n")
