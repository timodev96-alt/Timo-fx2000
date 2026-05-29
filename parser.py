import re
import numpy as np

def get_safe_namespace(extra: dict | None = None) -> dict:
    ns = {
        "__builtins__": None,
        "np": np,
        "sin":   np.sin,
        "cos":   np.cos,
        "tan":   np.tan,
        "asin":  np.arcsin,
        "acos":  np.arccos,
        "atan":  np.arctan,
        "atan2": np.arctan2,
        "sinh":  np.sinh,
        "cosh":  np.cosh,
        "tanh":  np.tanh,
        "log":   np.log10,
        "ln":    np.log,
        "log2":  np.log2,
        "sqrt":  np.sqrt,
        "abs":   np.abs,
        "exp":   np.exp,
        "ceil":  np.ceil,
        "floor": np.floor,
        "sign":  np.sign,
        "pi":    np.pi,
        "e":     np.e,
        "inf":   np.inf,
    }
    if extra:
        ns.update(extra)
    return ns

_SYM_MAP = [
    ("π",    "pi"),
    ("^",    "**"),
    ("√(",   "sqrt("),
    ("√",    "sqrt"),
]

_FUNC_MAP = {
    "sin":  "sin",
    "cos":  "cos",
    "tan":  "tan",
    "asin": "asin",
    "acos": "acos",
    "atan": "atan",
    "sinh": "sinh",
    "cosh": "cosh",
    "tanh": "tanh",
    "log":  "log",
    "ln":   "ln",
    "log2": "log2",
    "sqrt": "sqrt",
    "abs":  "abs",
    "exp":  "exp",
    "ceil": "ceil",
    "floor":"floor",
    "sign": "sign",
}

def _apply_symbol_subs(expr: str) -> str:
    for sym, replacement in _SYM_MAP:
        expr = expr.replace(sym, replacement)
    expr = re.sub(r'(?<![a-zA-Z_])e(?![a-zA-Z_(])', 'e', expr)
    return expr


def _insert_implicit_multiplications(expr: str) -> str:
    tokens = list(expr)
    result = []
    n = len(tokens)

    i = 0
    while i < n:
        ch = tokens[i]
        result.append(ch)

        if i < n - 1:
            nxt = tokens[i + 1]

            left_is_number  = ch.isdigit() or ch == '.'
            left_is_close   = ch == ')'
            left_is_var     = ch.isalpha() or ch == '_'

            right_is_open   = nxt == '('
            right_is_var    = nxt.isalpha() or nxt == '_'
            right_is_number = nxt.isdigit() or nxt == '.'

            if (left_is_number or left_is_close) and right_is_open:
                result.append('*')
            elif left_is_number and right_is_var:
                result.append('*')
            elif left_is_close and (right_is_var or right_is_number):
                result.append('*')
        i += 1

    raw = "".join(result)
    return raw


def _balance_parens(expr: str) -> str:
    diff = expr.count('(') - expr.count(')')
    if diff > 0:
        expr += ')' * diff
    return expr


def clean_expression(expr: str) -> str:
    expr = expr.strip()
    expr = _apply_symbol_subs(expr)
    expr = _insert_implicit_multiplications(expr)
    expr = _balance_parens(expr)
    return expr

def detect_mode(raw: str) -> str:
    from config import EQ_MODE_STANDARD, EQ_MODE_PARAMETRIC, EQ_MODE_TANGENT

    s = raw.strip().lower()

    if ',' in raw:
        parts = [p.strip() for p in raw.split(',', 1)]
        if len(parts) == 2:
            if ('=' in parts[0] and 't' in parts[0].lower() and
                    '=' in parts[1] and 't' in parts[1].lower()):
                return EQ_MODE_PARAMETRIC

    if s.startswith("tangent(") or "@" in raw:
        return EQ_MODE_TANGENT

    return EQ_MODE_STANDARD

def parse_parametric(raw: str):
    try:
        parts = [p.strip() for p in raw.split(',', 1)]
        x_part, y_part = parts[0], parts[1]
        x_expr = y_expr = None
        for part in [x_part, y_part]:
            if '=' in part:
                var, expr = part.split('=', 1)
                var = var.strip().lower()
                if var == 'x':
                    x_expr = clean_expression(expr.strip())
                elif var == 'y':
                    y_expr = clean_expression(expr.strip())

        if x_expr is not None and y_expr is not None:
            return x_expr, y_expr
    except Exception:
        pass
    return None

def parse_tangent(raw: str):
    try:
        raw = raw.strip()

        m = re.match(r'tangent\((.+),\s*x\s*=\s*(.+)\)', raw, re.IGNORECASE)
        if m:
            base_expr = clean_expression(m.group(1).strip())
            x_val = float(eval(clean_expression(m.group(2).strip()),
                               get_safe_namespace()))
            return base_expr, x_val

        if '@' in raw:
            expr_part, x_part = raw.split('@', 1)
            expr_part = re.sub(r'^\s*y\s*=\s*', '', expr_part, flags=re.IGNORECASE)
            base_expr = clean_expression(expr_part.strip())
            m2 = re.match(r'\s*x\s*=\s*(.+)', x_part.strip(), re.IGNORECASE)
            if m2:
                x_val = float(eval(clean_expression(m2.group(1).strip()),
                                   get_safe_namespace()))
                return base_expr, x_val
    except Exception:
        pass
    return None

def split_standard(raw: str):
    raw = raw.strip()
    if '=' not in raw:
        raw = f"y={raw}"
    left, right = raw.split('=', 1)
    return clean_expression(left.strip()), clean_expression(right.strip())

def validate_expression(expr: str, variables: dict | None = None) -> tuple[bool, str]:
    ns = get_safe_namespace({
        "x": np.float64(1.0),
        "y": np.float64(1.0),
        "t": np.float64(1.0),
    })
    if variables:
        ns.update(variables)
    try:
        result = eval(expr, ns)
        if result is None:
            return False, "Expression returned None"
        return True, ""
    except ZeroDivisionError:
        return True, ""
    except Exception as ex:
        return False, str(ex)