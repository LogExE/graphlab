from tkinter import *
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

    def __init__(self):
        self.gr = Graph()
        self.dots = {}
        self.edge_first = None

        self.root = Tk()
        self.root.title("Graph viz")

        self.frm_main = ttk.Frame(self.root, padding=10)
        self.frm_main.grid()

        self.canv = Canvas(self.frm_main, width=800, height=600, bg='white')
        self.canv.grid(column=0, row=0)
        self.canv.bind("<Button-1>", self.canv_m1click)

        self.frm = ttk.Frame(self.frm_main)
        self.frm.grid(column=1, row=0)
        ttk.Button(self.frm, text="Open",
                   command=self.open_click).grid(column=0, row=0)
        self.lbl = ttk.Label(self.frm, text="-")
        self.lbl.grid(column=0, row=1)

    def run(self):
        self.root.mainloop()

    def open_click(self):
        with filedialog.askopenfile() as f:
            self.gr = Graph.load_from_file(f)

    def canv_m1click(self, ev):
        for (vert, (x, y)) in self.dots.items():
            if (x - ev.x) ** 2 + (y - ev.y) ** 2 <= GraphApp.VERTICE_RADIUS ** 2:
                self.add_edge(vert)
                break
        else:
            self.add_vert(ev.x, ev.y)
        self.redraw_graph()

    def redraw_graph(self):
        self.canv.delete("all")
        for vert in self.gr.get_vertices():
            x, y = self.dots[vert]
            for nei in self.gr.get_adjacent(vert):
                xn, yn = self.dots[nei]
                self.canv.create_line(x, y, xn, yn, width=GraphApp.EDGE_WIDTH)
            circle(x, y, GraphApp.VERTICE_RADIUS,
                   self.canv, fill=GraphApp.VERTICE_COLOR)
            self.canv.create_text(x, y, text=vert)

    def add_edge(self, vert):
        if self.edge_first is None:
            self.edge_first = vert
        else:
            weight = None
            if self.gr.is_weighted():
                weight = simpledialog.askstring(
                    "Adding edge", "What's the weight of it?")
            try:
                self.gr.add_edge(self.edge_first, vert, weight)
                self.edge_first = None
            except GraphOperationException as e:
                messagebox.showerror(title="Error!", message=e)

    def add_vert(self, x, y):
        ans = simpledialog.askstring(
            "Adding vertice", "What's the name of it?")
        if ans is None:
            return
        try:
            self.gr.add_vertex(ans)
            self.dots[ans] = (x, y)
        except GraphOperationException as e:
            messagebox.showerror(title="Error!", message=e)


GraphApp().run()
