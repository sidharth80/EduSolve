import math
from simpleeval import simple_eval, EvalWithCompoundTypes

UNIT_CONVERSIONS = {
    # Speed
    ("mph", "m/s"): lambda v: v * 0.44704,
    ("m/s", "mph"): lambda v: v / 0.44704,
    ("km/h", "m/s"): lambda v: v / 3.6,
    ("m/s", "km/h"): lambda v: v * 3.6,
    # Temperature
    ("c", "f"): lambda v: v * 9 / 5 + 32,
    ("f", "c"): lambda v: (v - 32) * 5 / 9,
    ("c", "k"): lambda v: v + 273.15,
    ("k", "c"): lambda v: v - 273.15,
    # Mass
    ("kg", "lbs"): lambda v: v * 2.20462,
    ("lbs", "kg"): lambda v: v / 2.20462,
    ("g", "kg"): lambda v: v / 1000,
    ("kg", "g"): lambda v: v * 1000,
    # Length
    ("m", "ft"): lambda v: v * 3.28084,
    ("ft", "m"): lambda v: v / 3.28084,
    ("km", "miles"): lambda v: v * 0.621371,
    ("miles", "km"): lambda v: v / 0.621371,
    ("cm", "m"): lambda v: v / 100,
    ("m", "cm"): lambda v: v * 100,
    # Energy
    ("j", "cal"): lambda v: v / 4.184,
    ("cal", "j"): lambda v: v * 4.184,
    ("kj", "j"): lambda v: v * 1000,
    ("j", "kj"): lambda v: v / 1000,
    # Pressure
    ("pa", "atm"): lambda v: v / 101325,
    ("atm", "pa"): lambda v: v * 101325,
    # Time
    ("s", "min"): lambda v: v / 60,
    ("min", "s"): lambda v: v * 60,
    ("min", "h"): lambda v: v / 60,
    ("h", "min"): lambda v: v * 60,
    ("h", "s"): lambda v: v * 3600,
    ("s", "h"): lambda v: v / 3600,
}

SAFE_NAMES = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "pi": math.pi,
    "e": math.e,
    "pow": math.pow,
    "floor": math.floor,
    "ceil": math.ceil,
}

TOOL_DEFINITIONS = [
    {
        "name": "calculate",
        "description": (
            "Evaluate a mathematical expression and return the numeric result. "
            "Supports standard arithmetic operators (+, -, *, /, **, %), "
            "and functions: sqrt, sin, cos, tan, log, log10, exp, abs, round, "
            "floor, ceil, pow, atan2. Constants: pi, e."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A valid math expression, e.g. '60 * 0.44704' or 'sqrt(9.8 * 2 * 45)'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "convert_units",
        "description": (
            "Convert a numeric value from one unit to another. "
            "Supported pairs — speed: mph↔m/s, km/h↔m/s; "
            "temperature: C↔F, C↔K; mass: kg↔lbs, g↔kg; "
            "length: m↔ft, km↔miles, cm↔m; energy: J↔cal, kJ↔J; "
            "pressure: Pa↔atm; time: s↔min↔h."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "The numeric value to convert"},
                "from_unit": {"type": "string", "description": "Source unit (case-insensitive), e.g. 'mph'"},
                "to_unit": {"type": "string", "description": "Target unit (case-insensitive), e.g. 'm/s'"},
            },
            "required": ["value", "from_unit", "to_unit"],
        },
    },
]


def calculate(expression: str) -> dict:
    try:
        # Split names into callables (functions) and plain values (constants)
        fns = {k: v for k, v in SAFE_NAMES.items() if callable(v)}
        consts = {k: v for k, v in SAFE_NAMES.items() if not callable(v)}
        evaluator = EvalWithCompoundTypes(functions=fns, names=consts)
        result = evaluator.eval(expression)
        return {"result": round(float(result), 6), "expression": expression}
    except Exception as e:
        return {"error": str(e), "expression": expression}


def convert_units(value: float, from_unit: str, to_unit: str) -> dict:
    key = (from_unit.lower(), to_unit.lower())
    if key in UNIT_CONVERSIONS:
        result = UNIT_CONVERSIONS[key](value)
        return {
            "result": round(result, 6),
            "from": f"{value} {from_unit}",
            "to": f"{round(result, 6)} {to_unit}",
        }
    return {
        "error": f"No conversion available from '{from_unit}' to '{to_unit}'. "
        f"Supported: {[f'{a}→{b}' for a, b in UNIT_CONVERSIONS]}"
    }


def dispatch_tool(name: str, inputs: dict) -> str:
    import json
    if name == "calculate":
        return json.dumps(calculate(**inputs))
    if name == "convert_units":
        return json.dumps(convert_units(**inputs))
    return json.dumps({"error": f"Unknown tool: {name}"})
