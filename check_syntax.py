
import py_compile
try:
    py_compile.compile('app.py', doraise=True)
    print("Sintaxis Correcta")
except py_compile.PyCompileError as e:
    print(f"Error de sintaxis: {e}")
except Exception as e:
    print(f"Otro error: {e}")
