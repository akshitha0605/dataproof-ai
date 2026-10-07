import ast
import sys
import io
import time
import math
import statistics
import datetime
import re
import pandas as pd
import numpy as np
import traceback

FORBIDDEN_MODULES = {
    'os', 'sys', 'subprocess', 'socket', 'requests', 'urllib', 'shutil', 
    'importlib', 'pathlib', 'ctypes', 'threading', 'multiprocessing',
    'builtins', 'codecs', 'pickle', 'shelve', 'dbm', 'winreg'
}

FORBIDDEN_FUNCTIONS = {
    'eval', 'exec', 'compile', 'globals', 'locals', 'vars',
    'getattr', 'setattr', 'delattr', 'input', 'breakpoint'
}

ALLOWED_IMPORTS = {
    'pandas': pd,
    'pd': pd,
    'numpy': np,
    'np': np,
    'math': math,
    'statistics': statistics,
    'datetime': datetime,
    're': re
}

FORBIDDEN_DUNDERS = {
    '__subclasses__', '__bases__', '__mro__', '__globals__', '__code__',
    '__closure__', '__builtins__', '__class__'
}

class SecurityValidator(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            base_name = alias.name.split('.')[0]
            if base_name in FORBIDDEN_MODULES or base_name not in ALLOWED_IMPORTS:
                self.errors.append(f"Import of module '{alias.name}' is blocked for security.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_name = node.module.split('.')[0]
            if base_name in FORBIDDEN_MODULES or base_name not in ALLOWED_IMPORTS:
                self.errors.append(f"Import from module '{node.module}' is blocked for security.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_FUNCTIONS:
                self.errors.append(f"Function '{node.func.id}' is forbidden.")
            elif node.func.id == 'open':
                self.errors.append("Direct file access via 'open()' is forbidden in sandbox code.")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_DUNDERS:
                self.errors.append(f"Access to special attribute '{node.func.attr}' is forbidden.")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr in FORBIDDEN_DUNDERS:
            self.errors.append(f"Access to restricted attribute '{node.attr}' is forbidden.")
        self.generic_visit(node)

def safe_import_wrapper(name, globals=None, locals=None, fromlist=(), level=0):
    base_name = name.split('.')[0]
    if base_name in FORBIDDEN_MODULES or base_name not in ALLOWED_IMPORTS:
        raise ImportError(f"Import of module '{name}' is restricted by DataProof AI security sandbox.")
    return ALLOWED_IMPORTS.get(base_name, __import__(name, globals, locals, fromlist, level))

def validate_code_security(code_str: str) -> tuple[bool, str]:
    """
    Statically analyzes code AST to ensure no dangerous operations exist.
    Returns (is_safe, error_message)
    """
    try:
        tree = ast.parse(code_str)
        validator = SecurityValidator()
        validator.visit(tree)
        if validator.errors:
            return False, "; ".join(validator.errors)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error in code: {e}"
    except Exception as e:
        return False, f"Code security analysis failed: {str(e)}"

def run_safe_code(code_str: str, execution_context: dict, timeout_seconds: float = 5.0) -> dict:
    """
    Executes Python code in a safe, isolated namespace with captured output.
    `execution_context` can contain variables like `df` or `dfs`.
    """
    is_safe, sec_error = validate_code_security(code_str)
    if not is_safe:
        return {
            "success": False,
            "error": f"Security Violation: {sec_error}",
            "stdout": "",
            "stderr": sec_error,
            "result": None,
            "execution_time_ms": 0
        }

    safe_globals = {
        "__builtins__": {
            "__import__": safe_import_wrapper,
            "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
            "enumerate": enumerate, "filter": filter, "float": float, "int": int,
            "isinstance": isinstance, "len": len, "list": list, "map": map,
            "max": max, "min": min, "pow": pow, "range": range, "round": round,
            "set": set, "slice": slice, "sorted": sorted, "str": str, "sum": sum,
            "tuple": tuple, "zip": zip, "print": print, "type": type, "True": True,
            "False": False, "None": None, "Exception": Exception, "ValueError": ValueError
        },
        "pd": pd,
        "pandas": pd,
        "np": np,
        "numpy": np,
        "math": math,
        "statistics": statistics,
        "datetime": datetime,
        "re": re
    }

    safe_locals = dict(execution_context)

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    start_time = time.perf_counter()

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        compiled = compile(code_str, filename="<analyzed_code>", mode="exec")
        exec(compiled, safe_globals, safe_locals)

        exec_time = (time.perf_counter() - start_time) * 1000.0
        result_val = safe_locals.get("result", None)

        return {
            "success": True,
            "error": None,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "result": result_val,
            "execution_time_ms": round(exec_time, 2)
        }

    except Exception as e:
        exec_time = (time.perf_counter() - start_time) * 1000.0
        tb = traceback.format_exc()
        return {
            "success": False,
            "error": str(e),
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue() + "\n" + tb,
            "result": None,
            "execution_time_ms": round(exec_time, 2)
        }
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
