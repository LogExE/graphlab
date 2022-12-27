import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

from graph import Graph, GraphOperationException


def circle(x, y, r, canv, **args):
    canv.create_oval(x - r, y - r, x + r, y + r, **args)


class GraphApp():
    VERTICE_RADIUS = 20
    VERTICE_COLOR = "white"
    EDGE_WIDTH = 5
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
        self.canv = tk.Canvas(self.frm_main, width=800, height=600, bg='white')
        self.canv.grid(column=0, row=0)
        self.canv.bind("<Button-1>", self.canv_m1click)
        self.frm = ttk.Frame(self.frm_main)
        self.frm.grid(column=1, row=0)

        self.graphs_var = tk.StringVar(self.root)
        self.graphs_var.trace("w", self.change_cur_graph)
        self.graphs_var.set(GraphApp.DEFAULT_GRAPH)
        self.graph_menu = ttk.OptionMenu(self.frm, self.graphs_var,
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
            self.add_graph(f.name, Graph.load_from_file(f))

    def canv_m1click(self, ev):
        for (vert, (x, y)) in self.cur_dots.items():
            if (x - ev.x) ** 2 + (y - ev.y) ** 2 <= GraphApp.VERTICE_RADIUS ** 2:
                self.add_edge(vert)
                break
        else:
            self.add_vertice(ev.x, ev.y)
        self.redraw_graph()

    def change_cur_graph(self, *args):
        self.cur_graph = self.graphs[self.graphs_var.get()]
        self.cur_dots = self.dots[self.graphs_var.get()]

    def get_graphs(self):
        return self.graphs.keys()

    def add_graph(self, name, graph):
        self.graphs[name] = graph
        print(*self.graph_menu["menu"])

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
        self.canv.create_line(
            x1, y1, x2, y2, width=GraphApp.EDGE_WIDTH, fill=GraphApp.EDGE_COLOR)

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
        except GraphOperationException as e:
            messagebox.showerror(title="Error!", message=e)


GraphApp().run()
