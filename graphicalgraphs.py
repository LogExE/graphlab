#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
import os
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
                 GraphApp.CANVAS_HEIGHT / 2) - 2 * GraphApp.VERTEX_RADIUS
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
    ADD_VERT="Adding vertex"
    ADD_EDGE="Adding edge"
    REMOVE_VERT="Removing vertex"
    REMOVE_EDGE="Removing edge"
    MOVE_VERT="Moving vertex"

# main class
class GraphApp():
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    VERTEX_RADIUS = 20
    VERTEX_COLOR = "white"
    EDGE_WIDTH = 1
    EDGE_COLOR = "green"
    EDGE_WEIGHT_COLOR = "blue"
    DEFAULT_GRAPH = "default"

    def __init__(self):
        # here come dicts
        # containing additional info for each individual graph
        self.graphs = {}
        # vertices coordinates
        self.dots = {}
        # actions to undo/redo
        self.actions = {}

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

        # canvas where we will draw graphs
        self.canv = tk.Canvas(self.frm_main, width=GraphApp.CANVAS_WIDTH,
                              height=GraphApp.CANVAS_HEIGHT, bg='white')
        self.canv.grid(column=0, row=1)
        # mouse actions
        self.canv.bind("<Button-1>", self.canv_m1click)

        # various buttons for graph actions + status label
        self.subfrm1 = ttk.Frame(self.frm_main)
        self.subfrm1.grid(column=1, row=1)
        self.status_var = tk.StringVar(self.root)
        self.status_lbl = ttk.Label(self.subfrm1, textvariable=self.status_var)
        self.status_lbl.grid()
        ttk.Button(self.subfrm1, text="Create vertex",
                   command=self.start_adding_vertex).grid()
        ttk.Button(self.subfrm1, text="Create edge",
                   command=self.start_adding_edge).grid()
        ttk.Button(self.subfrm1, text="Remove vertex",
                   command=self.start_removing_vertex).grid()
        ttk.Button(self.subfrm1, text="Remove edge",
                   command=self.start_removing_edge).grid()

        # button to open new file + graph selection
        self.subfrm2 = ttk.Frame(self.frm_main)
        self.subfrm2.grid(column=0, row=0, sticky='w')
        ttk.Button(self.subfrm2, text="New",
                   command=self.new_click).grid(column=0, row=0)
        ttk.Button(self.subfrm2, text="Open",
                   command=self.open_click).grid(column=1, row=0)
        ttk.Button(self.subfrm2, text="Save",
                   command=self.save_click).grid(column=2, row=0)
        self.graphs_var = tk.StringVar(self.root)
        self.graphs_var.trace("w", self.change_cur_graph)
        self.graph_menu = ttk.OptionMenu(self.subfrm2, self.graphs_var,
                                         None,
                                         *self.get_graphs())
        self.graph_menu.grid(column=3, row=0)


    def run(self):
        self.root.mainloop()

    def clear_state(self):
        self.state = {}
        self.status_var.set(AppState.IDLE)
        
    def change_state(self, new_state):
        for k in new_state:
            if k == "msg":
                continue
            self.state[k] = new_state[k]
        if 'msg' in new_state:
            self.status_var.set(new_state['msg'])
        
    def start_adding_vertex(self):
        self.change_state({
            "msg": AppState.ADD_VERT,    
        })

    def start_adding_edge(self):
        self.change_state({
            "msg": AppState.ADD_EDGE,
        })

    def start_removing_vertex(self):
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

    def new_click(self):
        name = simpledialog.askstring(
                "Adding graph", "Name the new graph")
        if name is None:
            return
        directed = messagebox.askyesno(message="Will it be directed?")
        weighted = messagebox.askyesno(message="Will it be weighted?")
        self.add_graph(name, Graph([("not_" if not directed else "") + "directed",
                                    ("not_" if not weighted else "") + "weighted"]), {})
        
    def open_click(self):
        with filedialog.askopenfile() as f:
            loaded_graph = Graph.load_from_file(f)
            name, _ = os.path.splitext(f.name)
            pos = self.load_positions(name + ".pos")
            if pos is None:
                pos = circle_dots(loaded_graph)
            self.add_graph(name, loaded_graph, pos)

    def save_click(self):
        name = self.graphs_var.get()
        self.cur_graph.save(name + ".txt")
        self.save_positions(name + ".pos")

    def load_positions(self, fname):
        if not os.path.exists(fname):
            return None
        dots = {}
        with open(fname) as f:
            for line in f:
                vert, x, y = line.split()
                dots[vert] = (int(x), int(y))
        return dots
        
    def save_positions(self, fname):
        with open(fname, "w") as f:
            for name, (x, y) in self.cur_dots.items():
                f.write(f"{name} {x} {y}\n")

    def try_vertex(self, px, py):
        for (vert, (x, y)) in self.cur_dots.items():
            if len2((x - px, y - py)) <= GraphApp.VERTEX_RADIUS:
                return vert
        return None
    
    def canv_m1click(self, ev):
        status = self.status_var.get()
        if status == AppState.IDLE:
            vert = self.try_vertex(ev.x, ev.y)
            if vert is not None:
                self.change_state({
                    "msg": AppState.MOVE_VERT,
                    "selected_vertex": vert
                })
        elif status == AppState.MOVE_VERT:
            self.cur_dots[self.state["selected_vertex"]] = (ev.x, ev.y)
            self.clear_state()
            self.redraw_graph()
        elif status == AppState.ADD_EDGE:
            vert = self.try_vertex(ev.x, ev.y)
            if vert is not None:
                if "selected_vertex" not in self.state:
                    self.change_state({
                        "selected_vertex": vert
                    })
                else:
                    self.add_edge(self.state["selected_vertex"], vert)
                    self.clear_state()
        elif status == AppState.ADD_VERT:
            self.add_vertex(ev.x, ev.y)
            self.clear_state()
        elif status == AppState.REMOVE_VERT:
            vert = self.try_vertex(ev.x, ev.y)
            if vert is not None:
                self.remove_vertex(vert)
                self.clear_state()
        elif status == AppState.REMOVE_EDGE:
            vert = self.try_vertex(ev.x, ev.y)
            if vert is not None:
                if "selected_vertex" not in self.state:
                    self.change_state({
                        "selected_vertex": vert
                    })
                else:
                    self.remove_edge(self.state["selected_vertex"], vert)
                    self.clear_state()

    def change_cur_graph(self, *args):
        self.cur_graph = self.graphs[self.graphs_var.get()]
        self.cur_dots = self.dots[self.graphs_var.get()]
        self.clear_state()
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
            self.draw_vertex(vert)

    def draw_vertex(self, vert):
        x, y = self.cur_dots[vert]
        draw_circle(x, y, GraphApp.VERTEX_RADIUS,
               self.canv, fill=GraphApp.VERTEX_COLOR)
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
            x1 + GraphApp.VERTEX_RADIUS * dir_x,
            y1 + GraphApp.VERTEX_RADIUS * dir_y,
            x2 - GraphApp.VERTEX_RADIUS * dir_x,
            y2 - GraphApp.VERTEX_RADIUS * dir_y,
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
            self.redraw_graph()
        except GraphOperationException as e:
            messagebox.showerror(title="Error!", message=e)

    def add_vertex(self, x, y):
        ans = simpledialog.askstring(
            "Adding vertex", "What's the name of it?")
        if ans is None:
            return
        try:
            self.cur_graph.add_vertex(ans)
            self.cur_dots[ans] = (x, y)
            self.redraw_graph()
        except GraphOperationException as e:
            messagebox.showerror(title="Error!", message=e)

    def remove_vertex(self, vert):
        try:
            self.cur_graph.remove_vertex(vert)
            del self.cur_dots[vert]
            self.redraw_graph()
        except GraphOperationException as e:
            messagebox.showerror(title="Error!", message=e)

    def remove_edge(self, vert1, vert2):
        try:
            self.cur_graph.remove_edge(vert1, vert2)
            self.redraw_graph()
        except GraphOperationException as e:
            messagebox.showerror(title="Error!", message=e)

    

# that's easy, right?
GraphApp().run()
