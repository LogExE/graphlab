#!/usr/bin/env python3

import os
import os.path
from graph import Graph, GraphException, GraphOperationException
from graph_tasks import (task1, task2, task3,
                         task4, task5, task6,
                         task7, task8, task9)

tasks = (task1, task2, task3, task4, task5, task6, task7, task8, task9)


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
    "copy": ["copy_name"],
    "create": ["attrib1", "attrib2", "name"],
    "to": ["to_name"],
    "rename": ["new_name"],
    "delete": [],
    "get_graphs": [],
    "get_tasks": [],
    "solve": ["task_num"],
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


default_name = "default"
graphs = {default_name: Graph()}
current = default_name

print("Please type \"cmds\" to see availible commands")

while True:
    line = None
    try:
        line = input("\n" + current + " ~> ")
    except EOFError:
        line = "exit"
        print(line)

    line = line.split()
    if len(line) == 0:
        continue
    cmd, *args = line
    # Checking if we know the command
    if cmd not in cmds:
        print("Unknown command!")
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
        verts = gr.get_vertices()
        directed = gr.is_directed()
        weighted = gr.is_weighted()

        print("Is directed:", directed)
        print("Is weighted:", weighted)

        print("Vertices:")
        print(" ".join(verts))

        print("Connections:")
        printed = set()
        for x in verts:
            adj = gr.get_adjacent(x)
            for y in adj:
                if not directed and (y, x) in printed:
                    continue
                msg = None
                if directed:
                    msg = f"{x} -> {y}"
                else:
                    msg = f"{x} <-> {y}"
                if weighted:
                    msg += f": {adj[y]}"
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
        [name] = args
        try:
            fname = name + ".txt"
            graphs[name] = Graph(fname)
            print("Loaded", fname)
        except FileNotFoundError:
            print("No such file!")
        except GraphException as e:
            print("File is invalid:", e)
    elif cmd == "save":
        fname = current + ".txt"
        if os.path.exists(fname):
            print(f"File \"{fname}\" exists. Overwrite it? (y/n)")
            try:
                ans = input()
                if ans == 'y':
                    gr.save(fname)
                    print("Wrote", fname)
                elif ans == 'n':
                    print("Didn't save the graph")
                else:
                    print("I'll count it as no")
            except EOFError:
                print("No input... Not saving then")
        else:
            gr.save(fname)
            print("Wrote", fname)
    elif cmd == "copy":
        [cname] = args
        if cname in graphs:
            print("Name already presents in list!")
        else:
            graphs[cname] = Graph(gr)
    elif cmd == "create":
        *attribs, name = args
        if name in graphs:
            print("Name already presents in list!")
        else:
            try:
                graphs[name] = Graph(attribs)
            except GraphException as e:
                print(e)
    elif cmd == "to":
        [to_name] = args
        if to_name in graphs:
            current = to_name
        else:
            print("No such graph!")
    elif cmd == "rename":
        [new_name] = args
        if current == default_name:
            print("Cannot rename default graph!")
        elif new_name in graphs:
            print("New name already presents in list!")
        else:
            graphs[new_name] = gr
            del graphs[current]
            current = new_name
    elif cmd == "delete":
        if current == default_name:
            print("Cannot delete default graph!")
        else:
            del graphs[current]
            current = default_name
    elif cmd == "get_graphs":
        print("There is: " + " ".join(graphs.keys()))
    elif cmd == "get_tasks":
        for i, task in enumerate(tasks, 1):
            print(f"Task {i}:", task.__doc__)
    elif cmd == "solve":
        [task_number] = args
        task = tasks[int(task_number) - 1]
        argc = task.__code__.co_argcount
        if argc > 1:
            print("Please, provide:")
            print(" ".join(task.__code__.co_varnames[1:argc]))
        try:
            if argc > 1:
                more_args = input().split()
            else:
                more_args = tuple()
            if len(more_args) != argc - 1:
                print("Invalid arguments!")
                continue
            res = task(gr, *more_args)
            if isinstance(res, Graph):
                graphs[f"task{task_number}"] = res
                print(f"Now go to graph task{task_number}")
            else:
                print("Answer:")
                print(res)
        except EOFError:
            print("No input... No answer!!!")
        except GraphException as e:
            print(e)
    elif cmd == "exit":
        break
