"""
AUTHOR:         YemotaY
Titel:          pysu logging
Beschreibung:   log/monitor/analyze/visualize
Letztes Update: 09.01.2024
Lizenz:         open source of course
"""

# IMPORTS
import os
import ast
import sys
import time
import json
import inspect 
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from typing import Any
from datetime import datetime
from matplotlib.widgets import CheckButtons
import re 


class pysu:
    """
    This is an advanced class to log/monitor/visualize even big chunks of logic,"fast".
    level       = level: 1 -> only errors,2 -> warnings, too, 3 -> Everything, 0=Nothing(No log, no trace and no profiler)\
    linked      = True/False if you want to analyze any linked classes, when activated add #TOLOG to the class\
    save        = True/False, Should everythong be written into a file?\
    visualize   = True/False To be done..
    refer example uses for better understanding.

    """
    def __init__(self, level=1, linked = True, save = True, visualize = False) -> None:
        if 0 > level < 3:
            raise Exception(f"Ungültiges Loglevel {level}")
        
        self.level = level  
        self.messages = []
        self.callstack = []

        if(level == 0): #logging can get heavy. so you can turn off like this
            return 

        self.FunctionProfiler = FunctionProfiler(save) # must be initiated and used as a decorator
        stack = inspect.stack() 
        self.caller = stack[1]  
        self.base_structs = PyClassScanner(self.caller.filename).run() 
        self.uml = self.generate_uml_diagram(self.base_structs)

        if(linked):
            linked_classes = self.find_linked_classes(self.caller.filename) # search for linked classes with #TOLOG
            if(not linked_classes):
                return
            for i in range(len(linked_classes)): # get linked imports, must be in same folder
                if(str(linked_classes[i]).find(".") != -1):
                    linked_classes[i] = str(linked_classes[i]).split(".")[0]
                    self.linked_structs = PyClassScanner(linked_classes[i]+".py").run()
                    self.base_structs = self.combine_structs(self.base_structs,self.linked_structs)
                    self.uml = self.generate_uml_diagram(self.base_structs)

        if(self.level == 3):   
            print("***********************************************************************")  
            print("FOUND CLASSES")           
            self.print_pretty(self.base_structs)
            print("***********************************************************************")  
            print("CREATED UML")
            print(self.uml)
            print("***********************************************************************")  

        if(save):
            with open("UML.txt","w") as f:
                f.write(self.uml)

        if(visualize): #To be done later
            pass
            #self.monitor_visualizer = MonitorVisualizer(self.classes_structs).main() #TBD LATER


    # Workers
    def info(self, message, console=False):
        """Takes an information and stores it into the message list, if console = True it gets printed instantly"""
        if self.level == 3:
            self.messages.append({"mID": 3, "msg": message, "ts": time.time()})
            if console:
                print(message)

    def warn(self, message, console=False):
        """Takes an warning and stores it into the message list, if console = True it gets printed instantly"""
        if self.level == 3 or self.level == 2:
            self.messages.append({"mID": 2, "msg": message, "ts": time.time()})
            if console:
                print(message)

    def error(self, message, console=True):
        """Takes an error and stores it into the message list, if console = True it gets printed instantly"""
        self.messages.append({"mID": 1, "msg": message, "ts": time.time()})
        if console:
            print(message)
    
    #Outputs
    def get_errors(self) -> list:
        """Returns a list with all errors"""
        return [eintrag for eintrag in self.messages if eintrag["mID"] == 1]

    def get_warns(self) -> list:
        """Returns a list with all warnings"""
        return [eintrag for eintrag in self.messages if eintrag["mID"] == 2]

    def get_infos(self) -> list:
        """Returns a list with all informations"""
        return [eintrag for eintrag in self.messages if eintrag["mID"] == 3]

    def show_logs(self):
        print("\n[LOGGINGS]")
        print(f"Loglevel {self.level}")
        if self.level == 1:
            for log in [eintrag for eintrag in self.messages if eintrag["mID"] == 1]:
                print(log["msg"])
        elif self.level == 2:
            for log in [eintrag for eintrag in self.messages if eintrag["mID"] == 1] + [eintrag for eintrag in self.messages if eintrag["mID"] == 2]:
                print(log["msg"])
        elif self.level == 3:
            for log in self.messages:
                print(log["msg"])

    def find_linked_classes(self, filename):
        """
        Opens the specified file and searches for imports of other classes, marked with the marker '#TOLOG'.
        Additional comments after '#TOLOG' are ignored.
        Args:
            filename (str)        = The path to the file to be parsed.
        Returns:
            linked_classes (list) = A list of strings containing the imported classes, marked with '#TOLOG'.
        """
        linked_classes = []

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Search each row for imports with #TOLOG
            for line in lines:
                # Regex, um den Import zu finden, z. B. `from modulename import classname #TOLOG ...`
                match = re.match(r'^(?:from\s+([\w\.]+)\s+import\s+([\w\*]+)|import\s+([\w\.]+))\s+#TOLOG(\s+.*)?$', line.strip())
                if match:
                    if match.group(1) and match.group(2):
                        # `from modulename import classname`
                        linked_classes.append(f"{match.group(1)}.{match.group(2)}")
                    elif match.group(3):
                        # `import modulename`
                        linked_classes.append(match.group(3))

        except FileNotFoundError:
            print(f"The {filename} file was not found.")
        except Exception as e:
            print(f"Ein Exception in find_linked_classes occured : {e}")

        return linked_classes
    
    def print_pretty(self,data):
        def format_method(method):
            params = ', '.join(param['name'] for param in method['parameters'])
            return f"{method['name']}({params})"

        def format_class(cls):
            methods_str = "\n  ".join(format_method(m) for m in cls['methods'])
            return f"Class: {cls['name']}\n  Methods:\n  {methods_str}"

        def format_call_hierarchy(hierarchy):
            return f"Function: {hierarchy['name']}\n  Calls:\n    " + "\n    ".join(callee['name'] for callee in hierarchy['callees'])

        formatted_classes = "\n".join(format_class(cls) for cls in data['Classes'])
        formatted_call_hierarchy = "\n".join(format_call_hierarchy(call) for call in data['CallHierarchy'])
        output = f"Classes:\n{formatted_classes}\n\nCall Hierarchy:\n{formatted_call_hierarchy}"
        print(output)

    # PEPs
    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return f"{cls}(level={self.level})"

    def __str__(self) -> str:
        return f"Loglevel:{self.level}\nMessages:{self.messages}\nMonitor->{self.profiler.logs}"

    def __len__(self) -> int:
        return len(self.messages)

    def __iter__(self) -> iter:
        return self.messages

    def __contains__(self, item) -> bool:
        return self.messages.__contains__(item)

    def __enter__(self) -> Any:  # Called at the beginning of a with block
        print("pysu: -> __enter__ called()")

    def __exit__(
        self, exc_type, exc_val, exc_tb
    ) -> Any:  # Called at the beginning of a with block
        print("pysu: -> __exit__ called()")

    def __call__(
        self,
    ) -> Any:  # Allows an instance of a class to be called as a function
        print("pysu: -> __call__ called()")

    # Workers

    def combine_structs(self,base, linked):
        """
        Combines 2 dicts and look out for empty lists, refer to readme for output
        Args:
            base (dict)   = return from PyClassScanner
            linked (dict) = return from PyClassScanner
        Returns:
            combined      = combined dict from base and linked
        """
        combined = base.copy()  
        combined['Classes'] = base['Classes'] + linked['Classes'] 
        seen_class_names = set()
        combined['Classes'] = [cls for cls in combined['Classes'] if not (cls['name'] in seen_class_names or seen_class_names.add(cls['name']))]

        combined['CallHierarchy'] = base['CallHierarchy'] + linked['CallHierarchy']
        seen_calls = set()  
        combined['CallHierarchy'] = [ch for ch in combined['CallHierarchy'] if not (str(ch) in seen_calls or seen_calls.add(str(ch)))]
        return combined

    def generate_uml_diagram(self, classes_structs):
        """
        Generates an textual UML diagramm of the incoming classes_structs
        Args:
            classes_structs (dict)   = The dictionary containing all scanned classes
        Returns:
            uml_output  (str)        = textual UML scheme
        """
        uml_output = []
        for class_entry in classes_structs.get("Classes", []):
            class_name = class_entry["name"]
            methods = class_entry.get("methods", [])
            uml_output.append(f"class {class_name} {{")
            for method in methods:
                method_name = method["name"]
                parameters = method["parameters"]
                param_str = ", ".join(
                    param["name"] for param in parameters
                ) 
                uml_output.append(f"    + {method_name}({param_str})")
            uml_output.append("}")
            uml_output.append("")  
        # Extract call hierarchy
        call_hierarchy = classes_structs.get("CallHierarchy", [])
        if call_hierarchy:
            uml_output.append("Call Hierarchy:")
            for call in call_hierarchy:
                caller = call["name"]
                callees = call.get("callees", [])
                # Format call relationships
                callee_names = [callee["name"] for callee in callees]
                callee_str = ", ".join(callee_names)
                uml_output.append(f"    {caller} -> {callee_str}")
        # Combine UML lines
        return "\n".join(uml_output)


# TBD Later, not happy rn
class MonitorVisualizer:
    def __init__(self, classes_structs):
        raise NotImplementedError
        self.classes_structs = classes_structs
        self.G = nx.Graph()
        self.pos = None
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.class_check_buttons = []
        self.class_check_status = {}
        self.create_graph()
        self.create_positions()
        self.draw_graph()

    def __str__(self) -> str:
        return f"MonitorVisualizer(classes_structs={self.classes_structs})"

    def create_graph(self):
        # Add classes, methods, and parameters to the graph
        for cls in self.classes_structs["Classes"]:
            class_name = cls["name"]
            self.G.add_node(class_name, type="class")
            # Add methods and parameters
            for method in cls["methods"]:
                method_name = method["name"]
                self.G.add_node(method_name, type="method", class_name=class_name)
                self.G.add_edge(class_name, method_name)
                for param in method["parameters"]:
                    param_name = param["name"]
                    self.G.add_node(
                        param_name, type="parameter", method_name=method_name
                    )
                    self.G.add_edge(method_name, param_name)

    def create_positions(self):
        """Create positions for nodes"""
        self.pos = {}
        angle_shift = 2 * np.pi / len(self.classes_structs["Classes"])
        for i, cls in enumerate(self.classes_structs["Classes"]):
            class_name = cls["name"]
            angle = angle_shift * i
            x = np.cos(angle)
            y = np.sin(angle)
            self.pos[class_name] = (x, y)
            method_count = len(cls["methods"])
            method_angle_shift = 2 * np.pi / max(1, method_count)
            for j, method in enumerate(cls["methods"]):
                method_name = method["name"]
                angle = method_angle_shift * j
                mx = x + np.cos(angle) * 0.5
                my = y + np.sin(angle) * 0.5
                self.pos[method_name] = (mx, my)
                param_count = len(method["parameters"])
                param_angle_shift = 2 * np.pi / max(1, param_count)
                for k, param in enumerate(method["parameters"]):
                    param_name = param["name"]
                    angle = param_angle_shift * k
                    px = mx + np.cos(angle) * 0.1
                    py = my + np.sin(angle) * 0.1
                    self.pos[param_name] = (px, py)

    def draw_graph(self):
        """Draw the nodes"""
        node_types = nx.get_node_attributes(self.G, "type")
        color_map = {
            "class": "skyblue",
            "method": "lightgreen",
            "parameter": "lightcoral",
        }
        node_color = [color_map[node_types[node]] for node in self.G.nodes]
        nx.draw(
            self.G,
            self.pos,
            with_labels=True,
            node_size=1500,
            node_color=node_color,
            font_size=7,
            ax=self.ax,
            node_shape="o",
            edge_color="gray",
        )
        self.add_check_buttons()
        plt.title("Class Structure Diagram")
        plt.show()

    def add_check_buttons(self):
        """Create check buttons for each class to toggle visibility"""
        classes = [cls["name"] for cls in self.classes_structs["Classes"]]
        self.class_check_status = {cls: True for cls in classes}

        ax_check = self.fig.add_axes([0.01, 0.2, 0.1, 0.6])
        self.class_check_buttons = CheckButtons(
            ax_check, classes, [True] * len(classes)
        )

        def toggle_class(label):
            if label in self.class_check_status:
                self.class_check_status[label] = not self.class_check_status[label]
                self.update_graph()

        self.class_check_buttons.on_clicked(toggle_class)

    def update_graph(self):
        """Clear the axis and redraw based on the current state of the check buttons"""
        self.ax.clear()
        self.ax.set_title("Class Structure Diagram")
        # Collect all visible nodes
        visible_classes = [
            cls for cls, status in self.class_check_status.items() if status
        ]
        visible_nodes = set(visible_classes)  # Start with the visible classes
        for cls in visible_classes: # Add methods and parameters of visible classes
            methods = [
                n
                for n, d in self.G.nodes(data=True)
                if d.get("type") == "method" and d.get("class_name") == cls
            ]
            visible_nodes.update(methods)
            for method in methods:
                params = [
                    n
                    for n, d in self.G.nodes(data=True)
                    if d.get("type") == "parameter" and d.get("method_name") == method
                ]
                visible_nodes.update(params)

        G_visible = self.G.subgraph(visible_nodes)# Create the subgraph with the collected visible nodes
        node_types = nx.get_node_attributes(G_visible, "type")# Redraw the graph
        color_map = {
            "class": "skyblue",
            "method": "lightgreen",
            "parameter": "lightcoral",
        }
        node_color = [color_map[node_types[node]] for node in G_visible.nodes]

        nx.draw(
            G_visible,
            self.pos,
            with_labels=True,
            node_size=1500,
            node_color=node_color,
            font_size=7,
            ax=self.ax,
            node_shape="o",
            edge_color="gray",
        )
        plt.draw()


class FunctionProfiler:
    def __init__(self,save):
        self.save = save
        self.logs = [] 

    def __str__(self):
        return f"FunctionProfiler()"

    def trace(self, func):
        """Wrapper, to observe handed function."""

        def wrapper(*args, **kwargs):
            start_time = time.time()
            aufruf_zeit = datetime.now().isoformat()
            vtrace = []
            vtrace.append(f"[PROFILER] Test of method: {func.__name__}")
            vtrace.append(f"[PROFILER] Starttime: {aufruf_zeit}")
            parameter_info = inspect.signature(func)
            vtrace.append(f"[PROFILER] Parameter-signature: {parameter_info}")
            vtrace.append(f"[PROFILER] Used parameters: args={args}, kwargs={kwargs}")
            def trace_func(frame, event, arg):
                if frame.f_code.co_name == "__init__": #return none, sooo..
                    return
                if event == "call":
                    vtrace.append(f"[TRACE] Stepping into: {frame.f_code.co_name}")
                elif event == "line":
                    lokale_variablen = frame.f_locals
                    try:
                        vtrace.append(f"[TRACE] Methods variables value change. {frame.f_lineno}: {lokale_variablen}")
                    except TypeError:
                        pass
                elif event == "return":
                    vtrace.append(f"[TRACE] Step out of function: {frame.f_code.co_name} with return: {arg}")
                return trace_func

            sys.settrace(trace_func)  # Aktivieren des Tracers
            try:
                ergebnis = func(*args, **kwargs)
            finally:
                sys.settrace(None)  # Deaktivieren des Tracers
            end_time = time.time()
            dauer = end_time - start_time
            vtrace.append(f"[PROFILER] Execution time: {dauer:.4f} seconds")
            vtrace.append(f"[PROFILER] Result: {ergebnis}")
            self.logs.append(
                {
                    "funktion": func.__name__,
                    "startzeit": aufruf_zeit,
                    "dauer": dauer,
                    "args": "-".join(map(str, args)),
                    "kwargs": kwargs,
                    "ergebnis": str(ergebnis),
                    "vtrace": vtrace 
                }
            )
            return ergebnis

        return wrapper

    def print_pretty_function_profile(self,data):
        def format_trace(trace):
            return '\n  '.join(trace)

        # Formatierte Ausgabe
        output = f"Function Profile:\n"
        output += f"Function: {data['funktion']}\n"
        output += f"Start Time: {data['startzeit']}\n"
        output += f"Duration: {data['dauer']} seconds\n"
        output += f"Arguments: {data['args']}\n"
        output += f"Keyword Arguments: {json.dumps(data['kwargs'], indent=4)}\n"
        output += f"Result: {data['ergebnis']}\n"
        # Formatierte Trace-Ausgabe
        if 'vtrace' in data:
            output += f"\nTrace Log:\n"
            output += format_trace(data['vtrace'])

        print(output)
        print("***********************************************************************") 

    def show_logs(self):
        """Shows all saved logs"""
        if(self.logs):
            print("[TRACE LOGS]")
            if(self.save):
                with open("TRACE.json", "w") as f:
                    f.write(str(self.logs).replace("'", '"'))
            for log in self.logs:
                self.print_pretty_function_profile(log)

class PyClassScanner:
    def __init__(self, input_filename):
        """
        Takes an filename and parses the classes out of the file
        Args:
            filename (path) = The path to the to scanning file
        """
        self.input_filename = input_filename
        self.classes = {}
        self.call_hierarchy = {}
        self.ouput_obj = {}

    def __str__(self):
        return f"PyClassScanner(input_filename={self.input_filename})"

    def _parse_file(self):
        """Parses the input Python file and extracts class definitions."""
        with open(self.input_filename, "r", encoding="utf-8", errors="ignore") as file:
            tree = ast.parse(file.read(), filename=self.input_filename)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = self._extract_methods(node)
                self.classes[node.name] = methods

    def _extract_methods(self, class_node):
        """
        Extracts methods and their parameters from a class node.
        Args:
            class_node (Any) = The scanned class nodes
        """
        methods = {}
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name
                parameters = [arg.arg for arg in item.args.args]
                docstring = ast.get_docstring(item)  # Get the docstring of the method
                methods[method_name] = {
                    "parameters": parameters,
                    "docstring": docstring,
                }
                self._track_calls(item)
        return methods

    def _track_calls(self, method_node):
        """
        Tracks method calls inside the method body from method nodes.
        Args:
            method_node (Any) = The scanned method nodes
        """
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    caller = method_node.name
                    callee = node.func.attr
                    if caller not in self.call_hierarchy:
                        self.call_hierarchy[caller] = []
                    self.call_hierarchy[caller].append(callee)

    def _measure_execution_time(self, method_node):
        """
        Measures the execution time of the given method.
        Args:
            method_node (Any) = The scanned method nodes
        """
        start_time = time.time()
        exec(compile(method_node, filename="<ast>", mode="exec"))# Execute the method standalone
        end_time = time.time()
        return end_time - start_time

    def _generate_json(self):
        """Generates a JSON representation of the class structure and call hierarchy."""
        diagram = {"Classes": []}
        for class_name, methods in self.classes.items():
            class_elem = {"name": class_name, "methods": []}
            for method_name, method_info in methods.items():
                method_elem = {
                    "name": method_name,
                    "parameters": [
                        {"name": param} for param in method_info["parameters"]
                    ],
                    "docstring": method_info["docstring"]
                    or "",  # Include docstring if it exists
                }
                class_elem["methods"].append(method_elem)
            diagram["Classes"].append(class_elem)
        diagram["CallHierarchy"] = []
        for caller, callees in self.call_hierarchy.items():
            caller_elem = {
                "name": caller,
                "callees": [{"name": callee} for callee in callees],
            }
            diagram["CallHierarchy"].append(caller_elem)
        return diagram

    def run(self):
        """WRAPPER Main function to generate the JSON diagram."""
        if not os.path.isfile(self.input_filename):
            raise FileNotFoundError(f"File {self.input_filename} not found.")

        self._parse_file()
        json_output = self._generate_json()
        self.ouput_obj = json_output
        return json_output


