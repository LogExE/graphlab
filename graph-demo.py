#!/usr/bin/env python

import os
from graph import Graph, GraphOperationException, GraphFormatException


def clear():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')
    else:
        print(("Dunno how to clear "
               "on your platform :("))


cmds = {
    "clear": [],
    "cmds": [],
    "print": [],
    "add_vertex": ["v"],
    "add_edge": ["v1", "v2", "?price"],
    "remove_vertex": ["v"],
    "remove_edge": ["v1", "v2"],
    "load": ["in_file"],
    "save": [],
    "copy": [],
    "create": ["attrib1", "attrib2", "name"],
    "switch": ["to_name"],
    "rename": ["new_name"],
    "delete": [],
    "get_graphs": [],
    "exit": []
}


def test_args(cmd, args):
    cnt = len(cmds[cmd])
    opt = sum(1 for x in cmds[cmd] if x[0] == '?')
    return cnt - opt <= len(args) <= cnt


def commands():
    print("Commands:")
    for cmd in cmds:
        print(cmd, *cmds[cmd])


graphs = {"default": Graph()}
current = "default"

commands()

while True:
    line = None
    try:
        line = input("cmd> ")
    except EOFError:
        line = "exit"
        print(line)

    line = line.split()
    if len(line) == 0:
        continue
    cmd, *args = line
    # Checking if we know the command
    if cmd not in cmds:
        print("Uknown command!")
        continue
    # Checking count of arguments
    if not test_args(cmd, args):
        print(f"Wrong usage of command \"{cmd}\"!")
        continue

    gr = graphs[current]
    if cmd == "clear":
        clear()
    elif cmd == "cmds":
        commands()
    elif cmd == "print":
        print(f"Graph \"{current}\"")
        print("Attributes:")
        print("; ".join(gr.attributes))
        print("Vertices:")
        for v in gr.vertices:
            print(v)
        print("Connections:")
        printed = set()
        for x in gr.vertices:
            for y, price in gr.vertices[x].items():
                if "not_weighted" in gr.attributes and (y, x) in printed:
                    continue
                if "not_directed" in gr.attributes:
                    msg = f"{x} <-> {y}"
                else:
                    msg = f"{x} -> {y}"
                if "weighted" in gr.attributes:
                    msg += f": {price}"
                print(msg)
                printed.add((x, y))
    elif cmd == "add_vertex":
        try:
            gr.add_vertex(*args)
        except GraphOperationException as e:
            print(e)
    elif cmd == "remove_vertex":
        try:
            gr.remove_vertex(*args)
        except GraphOperationException as e:
            print(e)
    elif cmd == "add_edge":
        try:
            gr.add_edge(*args)
        except GraphOperationException as e:
            print(e)
    elif cmd == "remove_edge":
        try:
            gr.remove_edge(*args)
        except GraphOperationException as e:
            print(e)
    elif cmd == "load":
        [path] = args
        name = os.path.splitext(path)[0]
        try:
            graphs[name] = Graph(path)
            print("Loaded", name)
        except FileNotFoundError:
            print("No such file!")
        except GraphFormatException as e:
            print("File is invalid:", e)
    elif cmd == "save":
        name = current + ".txt"
        gr.save(name)
        print("Wrote", name)
    elif cmd == "copy":
        n = 1
        pref = current + "_copy"
        while pref + str(n) in graphs:
            n += 1
        name = pref + str(n)
        graphs[name] = Graph(gr)
        print(f"Copied: \"{name}\"")
    elif cmd == "create":
        *attribs, name = args
        if name in graphs:
            print("Name already presents in list!")
        else:
            try:
                graphs[name] = Graph(attribs)
            except GraphFormatException as e:
                print(e)
    elif cmd == "switch":
        [to_name] = args
        if to_name in graphs:
            current = to_name
        else:
            print("No such graph!")
    elif cmd == "rename":
        [new_name] = args
        if current == "default":
            print("Cannot rename default graph!")
        elif new_name in graphs:
            print("New name already presents in list!")
        else:
            graphs[new_name] = gr
            del graphs[current]
            current = new_name
    elif cmd == "delete":
        if current == "default":
            print("Cannot delete default graph!")
        else:
            del graphs[current]
            current = "default"
    elif cmd == "get_graphs":
        print("There is: " + "; ".join(graphs.keys()))
    elif cmd == "exit":
        break
