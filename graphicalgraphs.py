from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog

from graph import Graph

gr = Graph()


def canv_click(ev):
    ans = simpledialog.askstring("Adding vertice", "What's the name of it?")
    if ans is None:
        return
    circle(ev.x, ev.y, 20)


def circle(x, y, r):
    global canv
    canv.create_oval(x - r, y - r, x + r, y + r)


def open_click():
    global gr
    with filedialog.askopenfile() as f:
        gr = Graph.load_from_file(f)


root = Tk()
root.title("Graphs")
frm = ttk.Frame(root, padding=10)
frm.grid()

canv = Canvas(frm, width=800, height=600, bg='white')
canv.grid(column=0, row=0)
canv.bind("<Button-1>", canv_click)
ttk.Button(frm, text="Open", command=open_click).grid(column=1, row=0)
ttk.Label(frm, text="Hello World!").grid(column=1, row=1)

root.mainloop()
