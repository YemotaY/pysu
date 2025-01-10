from pysu import pysu
import time
import traceback

from helper import helper #TOLOG

log = pysu(level=3,linked=True,save=True,visualize=False)#IF nothing linked, it needs to be turned off!!
profiler = log.FunctionProfiler

class a:
    def __init__(self) -> None:
        self.endergebnis = 0

    @profiler.trace
    def example_function1(self,x, y):
        zwischen_ergebnis = x + y
        endergebnis = zwischen_ergebnis * 2
        return endergebnis

class b:
    def __init__(self) -> None:
        pass

    @profiler.trace
    def example_function2(self,a, b, c=1):
        time.sleep(0.5)  # Simuliert eine längere Ausführungszeit
        return (a + b) * c

try:

    log.info("ich bin nur eine info, will dem entwickler was sagen bei zeiten")
    log.warn("ich bin eine warnung, schau mal lieber")
    #log.error("ich bin ein Fehler, wegen mir ist das Programm zum abbruch gekommen")

    """ZU TESTEN / UMBAUEN"""
    a = a()
    b = b()
    
    result1 = a.example_function1(5, 3)
    result2 = b.example_function2(2, 4, c=3)# Funktionen ausführen
    profiler.show_logs()# Logs anzeigen


except Exception as e:
    print(traceback.format_exc())
    print(f"PYSU-MAIN: An exception occurred {e}")
