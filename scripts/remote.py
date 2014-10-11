__author__ = 'christian'
from pynetworktables import *
import time
import threading
import json
import copy
import math
from tkinter import *
from tkinter import ttk

ip = sys.argv[1]
NetworkTable.SetIPAddress(ip)
NetworkTable.SetClientMode()
NetworkTable.Initialize()

table = NetworkTable.GetTable("framework_remote")


root = Tk()
root.title("Framework Remote")
root.resizable(width=0, height=0)
mainframe = ttk.Frame(root, padding="20 20 20 20")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

modlist = list()
currentmod = "none"
commands = dict()
commandindex = int(1)

modframe = ttk.Frame(mainframe, relief=RAISED, padding="20 20 20 20")
modframe.grid(column=2, row=0, sticky=(N, W, E, S))
modframe.columnconfigure(0, weight=1)
modframe.rowconfigure(0, weight=1)
die = False


class TreeList():

    def blank_callback(self, x):
        return True

    seltrig = False
    callback = blank_callback

    def __init__(self, frame, column1key, columns=None):
        if columns is not None:
            self.widget = ttk.Treeview(frame, columns=columns.keys)
        else:
            self.widget = ttk.Treeview(frame)
            columns = dict()

        self.column1key = column1key
        self.srclist = dict()
        self.listedsrclist = dict()
        self.ids = dict()
        self.columns = columns

    def update(self):
        for item in self.listedsrclist:
            if item not in self.srclist:
                self.widget.delete(self.ids[item])
        for item in self.srclist:
            if item not in self.listedsrclist:
                self.ids[item] = self.widget.insert("", END, text=self.srclist[item][self.column1key], tags=(item, "module"))
                self.widget.tag_bind(item, sequence="<1>", callback=self.callback)
            values = list()
            for column in self.columns:
                values.append(self.srclist[item][self.columns[column]])
            self.widget.item(self.ids[item], values=values)
        self.listedsrclist = copy.copy(self.srclist)

    def onSelect(self, callback):
        for item in self.listedsrclist:
            self.widget.tag_bind(item, sequence="<1>", callback=callback)
        self.seltrig = True
        self.callback = callback

    def __getattr__(self, item):
        return getattr(self.widget, item)


def on_select(e):
    threading.Thread(target=mod_selected).start()


modlist_widget = TreeList(mainframe, "filename", columns={"name": "name"})
modlist_widget.grid(column=0, row=0, sticky=(N, S))
modlist_widget.heading("#0", text="Filename")
modlist_widget.column("#0", width=300)
modlist_widget.heading("#1", text="Name")
modlist_widget.column("#1", width=100)
modlist_widget.onSelect(on_select)

proclist_widget = TreeList(modframe, "name", columns={"Time Running": "timerunning"})

proclist_widget.grid(column=0, row=1, sticky=W)
proclist_widget.heading("#0", text="Process")
proclist_widget.column("#0", width=75)
proclist_widget.heading("#1", text="Age")
proclist_widget.column("#1", width=50)

sublist_widget = TreeList(modframe, "name")
sublist_widget.grid(column=0, row=2, sticky=W)
sublist_widget.heading("#0", text="fallbacks")
sublist_widget.column("#0", width=300)

modulelable = Label(modframe, text="Module")
modulelable.grid(column=2, row=0, sticky=N)

filenamelable = Label(modframe, text="Module")
filenamelable.grid(column=0, row=0, sticky=N)


def reload_mod():
    global commandindex
    commands[commandindex] = {"command": "reload module", "target": currentmod}
    commandindex += 1

def unload_mod():
    global commandindex
    commands[commandindex] = {"command": "unload module", "target": currentmod}
    commandindex += 1

buttongrid = ttk.Frame(modframe, padding="10 10 10 10")
buttongrid.grid(column=2, row=1, sticky=(N, S, E, W))

reload_button = ttk.Button(buttongrid, text="Reload Module", command=reload_mod)
reload_button.grid(column=0, row=0, sticky=N)

unload_button = ttk.Button(buttongrid, text="Unload Module", command=unload_mod)
unload_button.grid(column=0, row=1, sticky=N)

loadgrid = ttk.Frame(mainframe, padding="10 10 10 10")
loadgrid.grid(column=0, row=1, sticky=(N, S, E, W))

modname = StringVar()
modtoload = ttk.Entry(loadgrid, textvariable=modname)
modtoload.grid(column=0, row=0, sticky=(N, S, E, W))


def load_module():
    global commandindex
    commands[commandindex] = {"command": "load module", "target": modname.get()}
    commandindex += 1


loadmod_button = ttk.Button(loadgrid, text="Load Module", command=load_module)
loadmod_button.grid(column=1, row=0, sticky=(N, S, E))

def mod_selected():
    time.sleep(.01)
    global currentmod
    focus = modlist_widget.focus()

    for mod in modlist:
        modid = modlist_widget.ids[mod]
        if modid == focus:
            currentmod = mod

    proclist_widget.srclist = modlist[currentmod]["runningTasks"]
    proclist_widget.update()


def run():
    global modlist, commandindex, currentmod
    while not die:
        try:
            loadedmods = json.loads(table.GetString("modlist"))
            modlist = dict()
            for mod in loadedmods:
                modsummary = json.loads(table.GetString("mod." + mod))
                modlist[mod] = modsummary
                if currentmod not in loadedmods:
                    currentmod = mod
                for proc in modsummary["runningTasks"]:
                    modsummary["runningTasks"][proc]["timerunning"] = "{}".format(math.ceil(time.time() - modsummary["runningTasks"][proc]["starttime"]))

            fallbacklist = dict()
            for i in range(len(modlist[currentmod]["fallbackList"])):
                fallbacklist[str(i) + currentmod] = {"name": modlist[currentmod]["fallbackList"][i]}

            modlist_widget.srclist = modlist
            modlist_widget.update()
            proclist_widget.srclist = modlist[currentmod]["runningTasks"]
            proclist_widget.update()
            sublist_widget.srclist = fallbacklist
            sublist_widget.update()
            modulelable["text"] = currentmod
            filenamelable["text"] = modlist[currentmod]["filename"]
            try:
                remoteindex = int(table.GetNumber("globalCommandIndex"))
                if commandindex < remoteindex:
                    commandindex = remoteindex
            except TableKeyNotDefinedException:
                pass

            #Handle commands
            if len(commands) > 4:
                keys = [item for item in commands.keys()]
                for key in keys:
                    if key < commandindex - 4:
                        del(commands[key])

            table.PutString('frameworkcommands', json.dumps(commands))

        except TableKeyNotDefinedException as e:
            print(e)
            time.sleep(2)
        time.sleep(.1)

threading.Thread(target=run).start()
root.mainloop()
NetworkTable.Shutdown()
die = True
