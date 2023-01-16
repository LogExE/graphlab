import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
import math
import random

from graph import Graph, GraphOperationException


def circle(x, y, r, canv, **args):
    canv.create_oval(x - r, y - r, x + r, y + r, **args)


def norm2(vec):
    x, y = vec
    length = len2(vec)
    return (x / length, y / length)


def len2(vec):
    x, y = vec
    return (x ** 2 + y ** 2) ** 0.5


def circle_dots(graph):
    radius = min(GraphApp.CANVAS_WIDTH / 2,
                 GraphApp.CANVAS_HEIGHT / 2) - 2 * GraphApp.VERTICE_RADIUS
    center_x = GraphApp.CANVAS_WIDTH / 2
    center_y = GraphApp.CANVAS_HEIGHT / 2

    dots = {}
    ang = 0
    verts = graph.get_vertices()
    step = 2 * math.pi / len(verts)
    for vert in verts:
        dots[vert] = (center_x + radius * math.cos(ang),
                      center_y + radius * math.sin(ang))
        ang += step

    return dots


def random_dots(graph):
    dots = {}
    verts = graph.get_vertices()
    for vert in verts:
        dots[vert] = (random.random() * GraphApp.CANVAS_WIDTH,
                      random.random() * GraphApp.CANVAS_HEIGHT)

    return dots


class GraphApp():
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    VERTICE_RADIUS = 20
    VERTICE_COLOR = "white"
    EDGE_WIDTH = 1
    EDGE_COLOR = "green"
    EDGE_WEIGHT_COLOR = "blue"
    DEFAULT_GRAPH = "default"

    def __init__(self):
        self.graphs = {GraphApp.DEFAULT_GRAPH: Graph()}
        self.dots = {GraphApp.DEFAULT_GRAPH: {}}
        self.actions = {GraphApp.DEFAULT_GRAPH: []}
        self.cur_graph = self.cur_dots = self.cur_actions = None
        self.edge_first = None

        self.root = tk.Tk()
        self.root.title("Graph viz")

        self.frm_main = ttk.Frame(self.root, padding=10)
        self.frm_main.grid()
        self.canv = tk.Canvas(self.frm_main, width=GraphApp.CANVAS_WIDTH,
                              height=GraphApp.CANVAS_HEIGHT, bg='white')
        self.canv.grid(column=0, row=0)
        self.canv.bind("<Button-1>", self.canv_m1click)
        self.canv.bind("<Button-3>", self.canv_m2click)
        self.frm = ttk.Frame(self.frm_main)
        self.frm.grid(column=1, row=0)

        self.status_lbl = ttk.Label(self.frm, text="-")
        self.status_lbl.grid(column=0, row=0)
        self.graph_lbl = ttk.Label(self.frm, text="graph label")
        self.graph_lbl.grid(column=0, row=1)
        self.graphs_var = tk.StringVar(self.root)
        self.graphs_var.trace("w", self.change_cur_graph)
        self.graphs_var.set(GraphApp.DEFAULT_GRAPH)
        self.graph_menu = ttk.OptionMenu(self.frm, self.graphs_var,
                                         GraphApp.DEFAULT_GRAPH,
                                         *self.get_graphs())
        self.graph_menu.grid(column=0, row=2)
        ttk.Button(self.frm, text="Open",
                   command=self.open_click).grid(column=0, row=3)
        ttk.Button(self.frm, text="Create vertice",
                   command=lambda: 42).grid(column=0, row=4)
        ttk.Button(self.frm, text="Create edge",
                   command=lambda: 42).grid(column=0, row=5)

    def run(self):
        self.root.mainloop()

    def open_click(self):
        with filedialog.askopenfile() as f:
            loaded_graph = Graph.load_from_file(f)
            self.add_graph(f.name, loaded_graph, circle_dots(loaded_graph))

    def canv_m1click(self, ev):
        for (vert, (x, y)) in self.cur_dots.items():
            if len2(((x - ev.x), (y - ev.y))) <= GraphApp.VERTICE_RADIUS:
                self.add_edge(vert)
                break
        else:
            self.add_vertice(ev.x, ev.y)

    def canv_m2click(self, ev):
        self.edge_first = None
        self.status_lbl.config(text="-")

    def change_cur_graph(self, *args):
        self.cur_graph = self.graphs[self.graphs_var.get()]
        self.cur_dots = self.dots[self.graphs_var.get()]
        self.redraw_graph()

    def get_graphs(self):
        return self.graphs.keys()

    def add_graph(self, name, graph, dots):
        self.graphs[name] = graph
        self.dots[name] = dots
        self.graph_menu["menu"].add_command(
            label=name, command=tk._setit(self.graphs_var, name))

    def redraw_graph(self):
        self.canv.delete("all")
        drawn_edges = set()
        for vert in self.cur_graph.get_vertices():
            for nei in self.cur_graph.get_adjacent(vert):
                if self.cur_graph.is_directed() \
                        or (nei, vert) not in drawn_edges:
                    self.draw_edge(vert, nei)
                    drawn_edges.add((vert, nei))
            self.draw_vertice(vert)

    def draw_vertice(self, vert):
        x, y = self.cur_dots[vert]
        circle(x, y, GraphApp.VERTICE_RADIUS,
               self.canv, fill=GraphApp.VERTICE_COLOR)
        self.canv.create_text(x, y, text=vert)

    def draw_edge(self, vert1, vert2):
        if vert1 == vert2:
            return
        x1, y1 = self.cur_dots[vert1]
        x2, y2 = self.cur_dots[vert2]
        ang = math.atan2(y2 - y1, x2 - x1)
        dir_x = math.cos(ang)
        dir_y = math.sin(ang)
        dir_x, dir_y = norm2((dir_x, dir_y))
        self.canv.create_line(
            x1 + GraphApp.VERTICE_RADIUS * dir_x,
            y1 + GraphApp.VERTICE_RADIUS * dir_y,
            x2 - GraphApp.VERTICE_RADIUS * dir_x,
            y2 - GraphApp.VERTICE_RADIUS * dir_y,
            width=GraphApp.EDGE_WIDTH, fill=GraphApp.EDGE_COLOR,
            arrow=tk.LAST if self.cur_graph.is_directed() else None)
        edge_length = len2((x1 - x2, y1 - y2))
        norm_x = 1
        norm_y = - dir_x / dir_y
        norm_x, norm_y = norm2((norm_x, norm_y))
        norm_x *= math.copysign(1, ang)
        norm_y *= math.copysign(1, ang)
        self.canv.create_text(x1 + edge_length / 2 * dir_x
                              + 10 * GraphApp.EDGE_WIDTH * norm_x,
                              y1 + edge_length / 2 * dir_y
                              + 10 * GraphApp.EDGE_WIDTH * norm_y,
                              text=self.cur_graph.get_edge_attr(vert1, vert2),
                              fill=GraphApp.EDGE_WEIGHT_COLOR)

    def add_edge(self, vert):
        if self.edge_first is None:
            self.edge_first = vert
            self.status_lbl.config(text="Connecting " + vert)
        else:
            attr = None
            if self.cur_graph.is_weighted():
                attr = simpledialog.askstring(
                    "Adding edge", "What's the value of it's attribute?")
            try:
                self.cur_graph.add_edge(self.edge_first, vert, attr)
                self.edge_first = None
                self.status_lbl.config(text="-")
                self.redraw_graph()
            except GraphOperationException as e:
                messagebox.showerror(title="Error!", message=e)

    def add_vertice(self, x, y):
        ans = simpledialog.askstring(
            "Adding vertice", "What's the name of it?")
        if ans is None:
            return
        try:
            self.cur_graph.add_vertex(ans)
            self.cur_dots[ans] = (x, y)
            self.redraw_graph()
        except GraphOperationException as e:
            messagebox.showerror(title="Error!", message=e)


GraphApp().run()
