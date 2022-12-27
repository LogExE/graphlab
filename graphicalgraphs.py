import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
import math

from graph import Graph, GraphOperationException


def circle(x, y, r, canv, **args):
    canv.create_oval(x - r, y - r, x + r, y + r, **args)


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


class GraphApp():
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    VERTICE_RADIUS = 20
    VERTICE_COLOR = "white"
    EDGE_WIDTH = 1
    EDGE_COLOR = "black"
    DEFAULT_GRAPH = "default"

    def __init__(self):
        self.graphs = {GraphApp.DEFAULT_GRAPH: Graph()}
        self.dots = {GraphApp.DEFAULT_GRAPH: {}}
        self.cur_graph = None
        self.cur_dots = None
        self.edge_first = None

        self.root = tk.Tk()
        self.root.title("Graph viz")

        self.frm_main = ttk.Frame(self.root, padding=10)
        self.frm_main.grid()
        self.canv = tk.Canvas(self.frm_main, width=GraphApp.CANVAS_WIDTH,
                              height=GraphApp.CANVAS_HEIGHT, bg='white')
        self.canv.grid(column=0, row=0)
        self.canv.bind("<Button-1>", self.canv_m1click)
        self.frm = ttk.Frame(self.frm_main)
        self.frm.grid(column=1, row=0)

        self.graphs_var = tk.StringVar(self.root)
        self.graphs_var.trace("w", self.change_cur_graph)
        self.graphs_var.set(GraphApp.DEFAULT_GRAPH)
        self.graph_menu = ttk.OptionMenu(self.frm, self.graphs_var, GraphApp.DEFAULT_GRAPH,
                                         *self.get_graphs())
        self.graph_menu.grid(column=0, row=0)
        ttk.Button(self.frm, text="Open",
                   command=self.open_click).grid(column=0, row=1)
        self.lbl = ttk.Label(self.frm, text="-")
        self.lbl.grid(column=0, row=2)

    def run(self):
        self.root.mainloop()

    def open_click(self):
        with filedialog.askopenfile() as f:
            loaded_graph = Graph.load_from_file(f)
            self.add_graph(f.name, loaded_graph, circle_dots(loaded_graph))

    def canv_m1click(self, ev):
        for (vert, (x, y)) in self.cur_dots.items():
            if (x - ev.x) ** 2 + (y - ev.y) ** 2 <= GraphApp.VERTICE_RADIUS ** 2:
                self.add_edge(vert)
                break
        else:
            self.add_vertice(ev.x, ev.y)

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
        for vert in self.cur_graph.get_vertices():
            for nei in self.cur_graph.get_adjacent(vert):
                self.draw_edge(vert, nei)
            self.draw_vertice(vert)

    def draw_vertice(self, vert):
        x, y = self.cur_dots[vert]
        circle(x, y, GraphApp.VERTICE_RADIUS,
               self.canv, fill=GraphApp.VERTICE_COLOR)
        self.canv.create_text(x, y, text=vert)

    def draw_edge(self, vert1, vert2):
        x1, y1 = self.cur_dots[vert1]
        x2, y2 = self.cur_dots[vert2]
        ang = math.atan2(y2 - y1, x2 - x1)
        norm_x = math.cos(ang)
        norm_y = math.sin(ang)
        length = (norm_x ** 2 + norm_y ** 2) ** 0.5
        norm_x /= length
        norm_y /= length
        self.canv.create_line(
            x1 + GraphApp.VERTICE_RADIUS * norm_x,
            y1 + GraphApp.VERTICE_RADIUS * norm_y,
            x2 - GraphApp.VERTICE_RADIUS * norm_x,
            y2 - GraphApp.VERTICE_RADIUS * norm_y,
            width=GraphApp.EDGE_WIDTH, fill=GraphApp.EDGE_COLOR,
            arrow=tk.LAST if self.cur_graph.is_directed() else None)
        edge_length = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        self.canv.create_text(x1 + edge_length / 2 * norm_x,
                              y1 + edge_length / 2 * norm_y,
                              text=self.cur_graph.get_weight(vert1, vert2))

    def add_edge(self, vert):
        if self.edge_first is None:
            self.edge_first = vert
        else:
            weight = None
            if self.cur_graph.is_weighted():
                weight = simpledialog.askstring(
                    "Adding edge", "What's the weight of it?")
            try:
                self.cur_graph.add_edge(self.edge_first, vert, weight)
                self.edge_first = None
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
