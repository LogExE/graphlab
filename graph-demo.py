
import graph
import os

def clear():
    if os.name == 'nt':
         os.system('cls')
    elif os.name == 'posix':
        os.system('clear')
    else:
        print('\n' * 100)

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
    "switch": ["to_name"],
    "rename": ["new_name"],
    "delete": [],
    "get_names": [],
    "get_current": [],
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

graphs = {"default": graph.Graph()}
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
    if cmd not in cmds:
        print("Uknown command!")
        continue
    if not test_args(cmd, args):
        print(f"Wrong usage of command \"{cmd}\"!")
        continue
    
    # We've got some input, time to process it!
    gr = graphs[current]
    if cmd == "clear":
        clear()
    elif cmd == "cmds":
        commands()
    elif cmd == "print":
        print("Connections:")
        print("\n".join(map(str, gr.vertices.items())))
        print("Prices:")
        print("\n".join(map(str, gr.prices.items())))
    elif cmd == "add_vertex":
        if not gr.add_vertex(*args):
            print("Vertex does already exist!")
    elif cmd == "remove_vertex":
        if not gr.remove_vertex(*args):
            print("No such vertex!")
    elif cmd == "add_edge":
        if not gr.add_edge(*args):
            print("That edge does already exist!")
    elif cmd == "remove_edge":
        if not gr.remove_edge(*args):
            print("No such edge!")
    elif cmd == "load":
        path = args[0]
        name = os.path.splitext(path)[0]
        try:
            graphs[name] = graph.Graph(path)
            print("Loaded", name)
        except FileNotFoundError:
            print("No such file!")
        except graph.GraphFormatException:
            print("File is invalid!")
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
        graphs[name] = graph.Graph(gr)
        print(f"Copied: \"{name}\"")
    elif cmd == "switch":
        to_name = args[0]
        if to_name in graphs:
            current = to_name
        else:
            print("No such graph!")
    elif cmd == "rename":
        new_name = args[0]
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
    elif cmd == "get_names":
        print("There is: " + " ".join(graphs.keys()))
    elif cmd == "get_current":
        print(f"Current graph: \"{current}\"")
    elif cmd == "exit":
        break
