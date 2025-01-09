# PYSU

## 0. Table of contents:
[Intro](#0)\
[Description](#1)\
[Structure](#2)\
[Install and Integrate](#3)\
[Examples](#4)\
[Badges](#5)\
[Contribution](#6)\
[Future](#7)\
[?](#8)


<a id="0"></a>

## 1. pysu logging
Advanced logging/tracing/analyzing and later on visualization classes.\
This project grew out of sheer neccessity. I did wrote an LIDAR driver for my robot with a huge simulation class including icp and some other stuff.\
Many hugely time dependant steps and some tricky brain twists leeded me to the decision to enrich this.


<a id="1"></a>

## 2. Project Description
This class can do following things:
- Takes logs trough `pysu.info()` `pysu.warn()` `pysu.error()` as a basic logger
- Show logs trough `pysu.get_info()` `pysu.get_warn()` `pysu.get_error()` 
- Analyze the classes,methods,parameters from the file pysu gets imported
- Analyze the linked classes,methods,parameters which are marked with #TOLOG after the import
- It can trace variables values
- It creates an textual UML scheme with a representation of all collected classes
- And later on the visualization will be implemented

<a id="2"></a>

## 3. Project structure
### /pysu
- /pysu.py -> main classes
- /examples.py -> small boilerplate to show
- /helper.py -> small external class to analyze along
- /requirements.txt -> all library out of my venv

<a id="3"></a>

## 4. Setup
Clone this git or just add the `pysu.py` to your project.

Install `pip install matplotlib`, `pip install networkx`, `pip install numpy`
either in your venv or globally.

After that you need to initiate it in your code like:
```python
from pysu import pysu
log = pysu(level=3,linked=True,save=True,visualize=False)
profiler = log.FunctionProfiler
```

### Initparams:
_level_= level: 1 -> only errors,2 -> warnings, too, 3 -> Everything, 0=Nothing(No log, no trace and no profiler)\
_linked_=True/False if you want to analyze any linked classes, when activated add #TOLOG to the class\
_save_=True/False, Should everythong be written into a file?\
_visualize_=True/False To be done..

From now on you use the `pysu.info()`,`pysu.warning()` and `pysu.error()` to log.\
Add: `@profiler.trace` one line above every method/function you want to trace.\
Refer to the examples for a boilerplate.

Console output:\
`get_errors() -> list`,`get_warns() -> list`,`get_infos() -> list`\
`profiler.show_logs()` will show the trace logs to console

<a id="4"></a>

## 5. Examples
### Call
```python
from pysu import pysu
import time
import traceback
from helper import helper #TOLOG

log = pysu(level=3,linked=True,save=True,visualize=False) #IF nothing linked, it needs to be turned off!!
profiler = log.FunctionProfiler

class a:
    def __init__(self) -> None:
        self.endergebnis = 0
    @profiler.trace #This marks the functions that will be traced 
    def example_function1(self,x, y):
        zwischen_ergebnis = x + y
        endergebnis = zwischen_ergebnis * 2
        return endergebnis

class b:
    def __init__(self) -> None:
        pass
    @profiler.trace
    def example_function2(self,a, b, c=1):
        time.sleep(0.5) #Delay
        return (a + b) * c

#All 3 functions cann be called with a message and a bool representing if the message should be printed at runtime
log.info("Im just an information, im possibly junking your storage")
log.warn("Im something that needs your attention, could leed to bad conditions")
log.error("Im an fully grown error/exception, the programm stopped because of me")

"""TESTING"""
a = a()
b = b()
result1 = a.example_function1(5, 3)
result2 = b.example_function2(2, 4, c=3) # Call functions
profiler.show_logs() # Show logs
```
### Output
JSON
```json
[
    {
        "funktion": "example_function1",
        "startzeit": "2025-01-09T20:37:40.958055",
        "dauer": 0.0,
        "args": "<__main__.a object at 0x000001862FA36DC0>-5-3",
        "kwargs": {},
        "ergebnis": "16",
        "vtrace": [
            "[PROFILER] Test of method: example_function1",
            "[PROFILER] Starttime: 2025-01-09T20:37:40.958055",
            "[PROFILER] Parameter-signature: (self, x, y)",
            "[PROFILER] Used parameters: args=(<__main__.a object at 0x000001862FA36DC0>, 5, 3), kwargs={}",
            "[TRACE] Stepping into: example_function1",
            "[TRACE] Methods variables value change. 16: {"self": <__main__.a object at 0x000001862FA36DC0>, "x": 5, "y": 3}",
            "[TRACE] Methods variables value change. 17: {"self": <__main__.a object at 0x000001862FA36DC0>, "x": 5, "y": 3, "zwischen_ergebnis": 8}",
            "[TRACE] Methods variables value change. 18: {"self": <__main__.a object at 0x000001862FA36DC0>, "x": 5, "y": 3, "zwischen_ergebnis": 8, "endergebnis": 16}",
            "[TRACE] Step out of function: example_function1 with return: 16",
            "[PROFILER] Execution time: 0.0000 seconds",
            "[PROFILER] Result: 16"
        ]
    },
    {
        "funktion": "example_function2",
        "startzeit": "2025-01-09T20:37:40.958055",
        "dauer": 0.5119993686676025,
        "args": "<__main__.b object at 0x000001862FA36EE0>-2-4",
        "kwargs": {
            "c": 3
        },
        "ergebnis": "18",
        "vtrace": [
            "[PROFILER] Test of method: example_function2",
            "[PROFILER] Starttime: 2025-01-09T20:37:40.958055",
            "[PROFILER] Parameter-signature: (self, a, b, c=1)",
            "[PROFILER] Used parameters: args=(<__main__.b object at 0x000001862FA36EE0>, 2, 4), kwargs={"c": 3}",
            "[TRACE] Stepping into: example_function2",
            "[TRACE] Methods variables value change. 26: {"self": <__main__.b object at 0x000001862FA36EE0>, "a": 2, "b": 4, "c": 3}",
            "[TRACE] Methods variables value change. 27: {"self": <__main__.b object at 0x000001862FA36EE0>, "a": 2, "b": 4, "c": 3}",
            "[TRACE] Step out of function: example_function2 with return: 18",
            "[PROFILER] Execution time: 0.5120 seconds",
            "[PROFILER] Result: 18"
        ]
    }
]
```
UML
```UML
class a {
    + __init__(self)
    + example_function1(self, x, y)
}
class b {
    + __init__(self)
    + example_function2(self, a, b, c)
}
class helper {
    + __init__(self)
    + method(self)
}
Call Hierarchy:
    example_function2 -> sleep
```

<a id="5"></a>

## 6. Badges
I want to keep it up to date and improve continiously. And badges are also pretty cool.

<a id="6"></a>

## 7. Contribute
If you want you can buy me a coffe later(Link follow soon).Better just grab your copy, improve it and show it to me!! [-:

<a id="7"></a>

## 8. Future
Following points are on the agenda for the future:
Fully translate it, excuse me for some german leftovers\
Prettify and make the JSON output ongoing compatible\
Implementing/Testing on linux\
Improve data quality and beautify the output a bit more\
Visualize everything in an Interactive map

.
.
.
<a id="8"></a>
# Leave the world a bit better and lovelier behind than you've stumbled into. <3