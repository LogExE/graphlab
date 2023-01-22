#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
import math
import random
from enum import Enum

from graph import Graph, GraphOperationException


# tkinter doesn't know how to draw circles...
def draw_circle(x, y, r, canv, **args):
    canv.create_oval(x - r, y - r, x + r, y + r, **args)

    
# vector ops
def norm2(vec):
    x, y = vec
    length = len2(vec)
    return (x / length, y / length)


def len2(vec):
    x, y = vec
    return (x ** 2 + y ** 2) ** 0.5


# generation functions
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


class AppState(str, Enum):
    IDLE="Idle"
    ADD_VERT="Adding vertice"
    ADD_EDGE="Adding edge"
    REMOVE_VERT="Removing vertice"
    REMOVE_EDGE="Removing edge"

# main class
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
        # here come dicts
        # containing additional info for each individual graph
        self.graphs = {GraphApp.DEFAULT_GRAPH: Graph()}
        # vertices coordinates
        self.dots = {GraphApp.DEFAULT_GRAPH: {}}
        # actions to undo/redo
        self.actions = {GraphApp.DEFAULT_GRAPH: []}

        self.state = {}
        # for easy access to current graph info later on
        self.cur_graph = self.cur_dots = self.cur_actions = None

        self.root = tk.Tk()
        self.root.title("Graph viz")

        # undo, redo actions
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)

        # main frame lol
        self.frm_main = ttk.Frame(self.root, padding=10)
        self.frm_main.grid()

        # button to open new file + graph selection
        self.subfrm1 = ttk.Frame(self.frm_main)
        self.subfrm1.grid(column=0, row=0, sticky='w')
        ttk.Button(self.subfrm1, text="Open",
                   command=self.open_click).grid(column=0, row=0)
        self.graphs_var = tk.StringVar(self.root)
        self.graphs_var.trace("w", self.change_cur_graph)
        self.graph_menu = ttk.OptionMenu(self.subfrm1, self.graphs_var,
                                         GraphApp.DEFAULT_GRAPH,
                                         *self.get_graphs())
        self.graph_menu.grid(column=1, row=0)

        # canvas where we will draw graphs
        self.canv = tk.Canvas(self.frm_main, width=GraphApp.CANVAS_WIDTH,
                              height=GraphApp.CANVAS_HEIGHT, bg='white')
        self.canv.grid(column=0, row=1)
        # mouse actions
        self.canv.bind("<Button-1>", self.canv_m1click)
        self.canv.bind("<Button-3>", self.canv_m2click)

        # various buttons for graph actions + status label
        self.subfrm2 = ttk.Frame(self.frm_main)
        self.subfrm2.grid(column=1, row=1)
        self.status_var = tk.StringVar(self.root)
        self.status_lbl = ttk.Label(self.subfrm2, textvariable=self.status_var)
        self.status_lbl.grid()
        ttk.Button(self.subfrm2, text="Create vertice",
                   command=self.start_adding_vertice).grid()
        ttk.Button(self.subfrm2, text="Create edge",
                   command=self.start_adding_edge).grid()
        ttk.Button(self.subfrm2, text="Remove vertice",
                   command=self.start_removing_vertice).grid()
        ttk.Button(self.subfrm2, text="Remove edge",
                   command=self.start_removing_edge).grid()

    def run(self):
        self.root.mainloop()

    def change_state(self, new_state):
        for k in new_state:
            self.state[k] = new_state[k]
        if 'msg' in new_state and hasattr(self, 'status_var'):
            self.status_var.set(new_state['msg'])
        
    def start_adding_vertice(self):
        self.change_state({
            "msg": AppState.ADD_VERT,    
        })

    def start_adding_edge(self):
        self.change_state({
            "msg": AppState.ADD_EDGE,
            "selected_vertice": None
        })

    def start_removing_vertice(self):
        self.change_state({
            "msg": AppState.REMOVE_VERT
        })

    def start_removing_edge(self):
        self.change_state({
            "msg": AppState.REMOVE_EDGE
        })
        
    def undo(self, ev):
        print("Undo!")
        
    def redo(self, ev):
        print("Redo!")
        
    def open_click(self):
        with filedialog.askopenfile() as f:
            loaded_graph = Graph.load_from_file(f)
            self.add_graph(f.name, loaded_graph, circle_dots(loaded_graph))

    def try_vertice(self, px, py):
        for (vert, (x, y)) in self.cur_dots.items():
            if len2((x - px, y - py)) <= GraphApp.VERTICE_RADIUS:
                return vert
        return None
    
    def canv_m1click(self, ev):
        if self.status_var.get() == AppState.ADD_EDGE:
            vert = self.try_vertice(ev.x, ev.y)
            if vert is not None:
                if self.state["selected_vertice"] is None:
                    self.change_state({
                        "selected_vertice": vert
                    })
                else:
                    self.add_edge(self.state["selected_vertice"], vert)
                    self.change_state({
                        "msg": AppState.IDLE
                    })
        elif self.status_var.get() == AppState.ADD_VERT:
            self.add_vertice(ev.x, ev.y)
            self.change_state({
                "msg": AppState.IDLE
            })

    def canv_m2click(self, ev):
        self.edge_first = None
        self.status_lbl.config(text="-")

    def change_cur_graph(self, *args):
        self.cur_graph = self.graphs[self.graphs_var.get()]
        self.cur_dots = self.dots[self.graphs_var.get()]
        self.selected_vertice = None
        self.change_state({
            "msg": AppState.IDLE
        })
        self.redraw_graph()

    def get_graphs(self):
        return self.graphs.keys()

    def add_graph(self, name, graph, dots):
        self.graphs[name] = graph
        self.dots[name] = dots
        self.graph_menu["menu"].add_command(
            label=name, command=tk._setit(self.graphs_var, name))

    def redraw_graph(self):
        if not hasattr(self, 'canv'):
            return
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
        draw_circle(x, y, GraphApp.VERTICE_RADIUS,
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

    def add_edge(self, vert1, vert2):
        attr = None
        if self.cur_graph.is_weighted():
            attr = simpledialog.askstring(
                "Adding edge", "What's the value of it's attribute?")
        try:
            self.cur_graph.add_edge(vert1, vert2, attr)
            self.selected_vertice = None
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


# that's easy, right?
GraphApp().run()
