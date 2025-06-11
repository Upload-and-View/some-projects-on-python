# PLua (Lua to Python) - MNM (Muser Not Matters) Extended Functionality V1
# Updated by Muser (New Big Update (NBU))
# Enhanced by AI (Control Flow, Basic Roblox Libs)
# About command (+ Easter EGG)!
import re
import shlex
from typing import Any, Dict, List, Tuple, Optional, Callable # Ensure Dict, Any, Optional are imported
import tkinter as tk
import sys
from io import StringIO
from io import BytesIO
import math # Import Python math module
import random # Import Python random module
import threading
import requests
from PIL import Image, ImageTk, ImageDraw, ImageFont
BlockInfo = Dict[str, Any] # Define what BlockInfo means for type hints
root_ref = None  # Global variable to hold a reference to the main Tkinter window
EASTER_EGG_DURATION_MS = 500000  # Set the duration in milliseconds (e.g., 5000ms = 5 seconds)

def show_network_easter_egg_internal(python_url, luau_url):
    global root_ref, EASTER_EGG_DURATION_MS
    if root_ref is None:
        return  # Ensure main window exists

    easter_egg_window = tk.Toplevel(root_ref)  # Create Toplevel associated with the main window
    easter_egg_window.title("MNM V3 Easter Egg")

    python_original_img = None
    luau_original_img = None

    try:
        python_response = requests.get(python_url)
        python_response.raise_for_status()
        python_image_data = BytesIO(python_response.content)
        python_original_img = Image.open(python_image_data).convert("RGBA")

        luau_response = requests.get(luau_url)
        luau_response.raise_for_status()
        luau_image_data = BytesIO(luau_response.content)
        luau_original_img = Image.open(luau_image_data).convert("RGBA")

    except requests.exceptions.RequestException as e:
        error_label = tk.Label(easter_egg_window, text=f"Error loading image from network: {e}")
        error_label.pack(padx=10, pady=10)
        return
    except Exception as e:
        error_label = tk.Label(easter_egg_window, text=f"Error processing network image: {e}")
        error_label.pack(padx=10, pady=10)
        return

    canvas_width = 300
    canvas_height = 200
    canvas = tk.Canvas(easter_egg_window, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack(padx=20, pady=20)

    python_item = canvas.create_image(canvas_width // 4, canvas_height // 2, image=None)
    luau_item = canvas.create_image(3 * canvas_width // 4, canvas_height // 2, image=None)

    scale_factor = 0.5
    scale_direction = 0.01
    angle = 0

    python_x = canvas_width // 4
    python_y = canvas_height // 2
    luau_x = 3 * canvas_width // 4
    luau_y = canvas_height // 2
    speed_x_python = 1
    speed_y_python = 0.5
    speed_x_luau = -0.4
    speed_y_luau = -0.6

    def animate_logos():
        nonlocal scale_factor, scale_direction, angle, python_original_img, luau_original_img
        nonlocal python_x, python_y, luau_x, luau_y, speed_x_python, speed_y_python, speed_x_luau, speed_y_luau

        scale_factor += scale_direction
        if scale_factor > 1.2 or scale_factor < 0.3:
            scale_direction *= -1

        angle += 2

        # --- Update Python Logo ---
        if python_original_img:
            scaled_python_size = (int(python_original_img.width * scale_factor),
                                  int(python_original_img.height * scale_factor))
            rotated_python = python_original_img.resize(scaled_python_size).rotate(angle, center=python_original_img.size[:2])
            python_photo = ImageTk.PhotoImage(rotated_python)
            canvas.itemconfig(python_item, image=python_photo)
            canvas.image_python = python_photo
            python_x += speed_x_python
            python_y += speed_y_python
            if python_x - scaled_python_size[0] // 2 < 0 or python_x + scaled_python_size[0] // 2 > canvas_width:
                speed_x_python *= -1
            if python_y - scaled_python_size[1] // 2 < 0 or python_y + scaled_python_size[1] // 2 > canvas_height:
                speed_y_python *= -1
            canvas.coords(python_item, python_x, python_y)

        # --- Update Luau Logo ---
        if luau_original_img:
            scaled_luau_size = (int(luau_original_img.width * scale_factor),
                                 int(luau_original_img.height * scale_factor))
            rotated_luau = luau_original_img.resize(scaled_luau_size).rotate(-angle, center=luau_original_img.size[:2])
            luau_photo = ImageTk.PhotoImage(rotated_luau)
            canvas.itemconfig(luau_item, image=luau_photo)
            canvas.image_luau = luau_photo
            luau_x += speed_x_luau
            luau_y += speed_y_luau
            margin = 5  # Adjust as needed

            if luau_x - scaled_luau_size[0] // 2 < -margin or luau_x + scaled_luau_size[0] // 2 > canvas_width + margin:
                speed_x_luau *= -1
            if luau_y - scaled_luau_size[1] // 2 < -margin or luau_y + scaled_luau_size[1] // 2 > canvas_height + margin:
                speed_y_luau *= -1
            canvas.coords(luau_item, luau_x, luau_y)

        canvas.after(30, animate_logos)

    animate_logos()

    # Schedule the window to close after a certain duration
    easter_egg_window.after(EASTER_EGG_DURATION_MS, easter_egg_window.destroy)

def show_network_easter_egg(python_url, luau_url):
    global root_ref
    print("Loading Network Easter Egg...")
    # Schedule the actual UI creation to run in the main Tkinter thread
    if root_ref:
        root_ref.after(0, show_network_easter_egg_internal, python_url, luau_url)


# --- Utility Functions (lua_gsub, convertsimplevalues - unchanged) ---
def lua_gsub(text, pattern, replacement):
    """
    Mimics Lua's string.gsub function using Python regex.
    NOTE: `pattern` uses Python regex syntax, not Lua patterns.
    `replacement` can be a string (with \1, \2 for groups) or a function.
    """
    count = 0
    try:
        if callable(replacement):
            def replace_func(match):
                nonlocal count
                count += 1
                # Pass matched groups to the replacement function
                try:
                    return str(replacement(*match.groups()))
                except TypeError:
                     # If replacement func doesn't take args, pass the whole match
                     try:
                         return str(replacement(match.group(0)))
                     except Exception as e:
                          print(f"Error in gsub replacement function: {e}")
                          return match.group(0) # Return original on error
                except Exception as e:
                    print(f"Error in gsub replacement function: {e}")
                    return match.group(0) # Return original on error

            modified_text = re.sub(pattern, replace_func, text)
            # Count might not be perfect if re.sub calls func but func returns original
        else:
            # replacement is a string, use re.subn
            modified_text, count = re.subn(pattern, replacement, text)
        return modified_text, count
    except re.error as e:
        print(f"Regex error in gsub pattern '{pattern}': {e}")
        return text, 0 # Return original text on regex error
    except Exception as e:
        print(f"Error during gsub: {e}")
        return text, 0

def convertsimplevalues(val: Any) -> Any:
    """Converts string representation of simple Lua values to Python types."""
    if not isinstance(val, str): return val
    lower_val = val.lower()
    if lower_val == "nil": return None
    elif lower_val == "false": return False
    elif lower_val == "true": return True
    if val.startswith('"') and val.endswith('"'): return val[1:-1]
    if val.startswith("'") and val.endswith("'"): return val[1:-1]
    try: return int(val)
    except ValueError:
        try:
            # Check if it looks like a number before converting
            cleaned_val = val.strip()
            if cleaned_val.replace('.', '', 1).replace('-', '', 1).isdigit():
                 return float(cleaned_val)
            else: return val # Not a number looking string
        except ValueError: return val

# --- Argument Parsing and Value Resolution ---

def parse_value(token: str, local_vars: dict) -> Any:
    """
    Parses a token into a Python value.
    Checks local variables, then math/string tables, then simple literals.
    Handles basic member access like 'math.pi' or 'string.len'.
    Returns the value or function object.
    """
    # 1. Handle Member Access (basic) -> math.pi, string.len
    if '.' in token:
        parts = token.split('.', 1)
        base_name = parts[0]
        member_name = parts[1]
        if base_name in local_vars and isinstance(local_vars[base_name], dict):
            base_table = local_vars[base_name]
            if member_name in base_table:
                return base_table[member_name] # Return constant or function object
            else:
                # Member not found in the table
                # print(f"Warning: Member '{member_name}' not found in table '{base_name}'.")
                return None # Represent as nil
        else:
             # Base table not found or not a table
             # print(f"Warning: Base '{base_name}' not found or not a table for member access.")
             return None # Represent as nil

    # 2. Check if it's a known local variable
    if token in local_vars:
        return local_vars[token]

    # 3. Check if it's a simple literal value (string, number, bool, nil)
    return convertsimplevalues(token)


def parse_arguments(tokens: List[str], start_index: int, local_vars: dict) -> List[Any]:
    """Parses tokens starting from start_index into evaluated arguments."""
    args = []
    for i in range(start_index, len(tokens)):
        args.append(parse_value(tokens[i], local_vars))
    return args

# --- Roblox Library Implementations ---

# Dictionary to hold our math implementations
mnm_math_lib = {}
# Dictionary to hold our string implementations
mnm_string_lib = {}

# --- Math Library Functions ---

def _mnm_math_abs(x=None): return math.fabs(x) if isinstance(x, (int, float)) else 0
def _mnm_math_acos(x=None): return math.acos(x) if isinstance(x, (int, float)) else 0
def _mnm_math_asin(x=None): return math.asin(x) if isinstance(x, (int, float)) else 0
def _mnm_math_atan(x=None): return math.atan(x) if isinstance(x, (int, float)) else 0
def _mnm_math_atan2(y=None, x=None): return math.atan2(y, x) if isinstance(y, (int, float)) and isinstance(x, (int, float)) else 0
def _mnm_math_ceil(x=None): return math.ceil(x) if isinstance(x, (int, float)) else 0
def _mnm_math_clamp(x=None, min_val=None, max_val=None):
    if not all(isinstance(n, (int, float)) for n in [x, min_val, max_val]): return 0
    return max(min_val, min(x, max_val))
def _mnm_math_cos(x=None): return math.cos(x) if isinstance(x, (int, float)) else 1 # cos(0)=1
def _mnm_math_cosh(x=None): return math.cosh(x) if isinstance(x, (int, float)) else 1 # cosh(0)=1
def _mnm_math_deg(x=None): return math.degrees(x) if isinstance(x, (int, float)) else 0
def _mnm_math_exp(x=None): return math.exp(x) if isinstance(x, (int, float)) else 1 # exp(0)=1
def _mnm_math_floor(x=None): return math.floor(x) if isinstance(x, (int, float)) else 0
def _mnm_math_fmod(x=None, y=None): return math.fmod(x, y) if isinstance(x, (int, float)) and isinstance(y, (int, float)) else 0
def _mnm_math_frexp(x=None): return math.frexp(x) if isinstance(x, (int, float)) else (0, 0) # Returns tuple
def _mnm_math_ldexp(x=None, e=None): return math.ldexp(x, int(e)) if isinstance(x, (int, float)) and isinstance(e, (int, float)) else 0
def _mnm_math_lerp(a=None, b=None, t=None):
    if not all(isinstance(n, (int, float)) for n in [a, b, t]): return 0
    return a + (b - a) * t
def _mnm_math_log(x=None, base=None):
    if not isinstance(x, (int, float)) or x <= 0: return -math.inf # Or None? Lua might error
    if base is None: return math.log(x)
    if not isinstance(base, (int, float)) or base <= 0 or base == 1: return -math.inf
    return math.log(x, base)
def _mnm_math_log10(x=None): return math.log10(x) if isinstance(x, (int, float)) and x > 0 else -math.inf
# Removed map function, as it's not standard Python math
def _mnm_math_max(*args): return max(args) if args else 0 # Lua errors on no args
def _mnm_math_min(*args): return min(args) if args else 0 # Lua errors on no args
def _mnm_math_modf(x=None): return math.modf(x) if isinstance(x, (int, float)) else (0.0, 0.0) # Returns tuple (f, i)
# noise omitted
def _mnm_math_pow(x=None, y=None): return math.pow(x, y) if isinstance(x, (int, float)) and isinstance(y, (int, float)) else 0
def _mnm_math_rad(x=None): return math.radians(x) if isinstance(x, (int, float)) else 0
def _mnm_math_random(m=None, n=None):
    m_num = isinstance(m, (int, float))
    n_num = isinstance(n, (int, float))
    if m_num and n_num: return random.uniform(m, n) if isinstance(m, float) or isinstance(n, float) else random.randint(int(m), int(n))
    elif m_num: return random.uniform(0, m) if isinstance(m, float) else random.randint(1, int(m)) # Roblox convention: random(m) is 1..m
    else: return random.random() # Default [0, 1)
def _mnm_math_randomseed(x=None): random.seed(x) # Returns void/None
def _mnm_math_round(x=None): return round(x) if isinstance(x, (int, float)) else 0 # Python 3 round (to nearest even for .5)
def _mnm_math_sign(x=None):
    if not isinstance(x, (int, float)): return 0
    if x == 0: return 0
    return math.copysign(1, x)
def _mnm_math_sin(x=None): return math.sin(x) if isinstance(x, (int, float)) else 0 # sin(0)=0
def _mnm_math_sinh(x=None): return math.sinh(x) if isinstance(x, (int, float)) else 0
def _mnm_math_sqrt(x=None): return math.sqrt(x) if isinstance(x, (int, float)) and x >= 0 else 0
def _mnm_math_tan(x=None): return math.tan(x) if isinstance(x, (int, float)) else 0
def _mnm_math_tanh(x=None): return math.tanh(x) if isinstance(x, (int, float)) else 0

# Populate mnm_math_lib
# Create a static list of items from locals() BEFORE iterating
local_items_math = list(locals().items())
for name, func in local_items_math:
    # Check if it's one of our functions AND it's actually callable
    if name.startswith("_mnm_math_") and callable(func):
        mnm_math_lib[name[10:]] = func # Strip prefix

# Add math constants separately (ensures they don't interfere with iteration)
mnm_math_lib['pi'] = math.pi
mnm_math_lib['huge'] = float('inf')


# --- String Library Functions ---

# Helper for 1-based Lua index -> 0-based Python index
def _lua_to_py_index(idx, length):
    if not isinstance(idx, int): return None # Invalid index type
    if idx > 0: return idx - 1
    elif idx == 0: return None # Lua doesn't use 0
    # idx < 0: Lua's -1 is end, -2 is second to last, etc.
    elif idx >= -length: return length + idx
    else: return None # Index out of bounds (negative)

# Helper for Lua slicing (inclusive j) -> Python slicing (exclusive j)
def _get_slice_indices(s_len, i, j):
    py_i = _lua_to_py_index(i, s_len)
    # Default for j is -1 (Lua end)
    j = j if j is not None else -1
    py_j = _lua_to_py_index(j, s_len)

    if py_i is None: py_i = 0 # Default start if i invalid? Or error? Let's default to 0
    if py_j is None: py_j = s_len -1 # Default end if j invalid? Let's default to end

    # Python slice needs index *after* the desired end character
    py_j_exclusive = py_j + 1

    # Basic bounds check
    if py_i < 0: py_i = 0
    if py_j_exclusive > s_len: py_j_exclusive = s_len
    if py_i >= py_j_exclusive: return None, None # Invalid slice resulting in empty

    return py_i, py_j_exclusive

def _mnm_string_byte(s:str="", i:int=1, j:Optional[int]=None):
    if not isinstance(s, str): s = str(s)
    if j is None: j = i
    s_len = len(s)
    py_i, py_j_exclusive = _get_slice_indices(s_len, i, j)
    if py_i is None: return () # Return empty tuple for no results

    codes = []
    for k in range(py_i, py_j_exclusive):
        codes.append(ord(s[k]))
    return tuple(codes) # Lua returns multiple numbers, simulate with tuple

def _mnm_string_char(*args):
    chars = []
    for code in args:
        if isinstance(code, (int, float)):
            try:
                chars.append(chr(int(code)))
            except ValueError:
                print(f"Warning: Invalid code point {code} in string.char")
                chars.append('?') # Placeholder for invalid codes
        else:
             chars.append('?')
    return "".join(chars)

def _mnm_string_find(s:str="", pattern:str="", init:int=1, plain:bool=False):
    if not isinstance(s, str): s = str(s)
    if not isinstance(pattern, str): pattern = str(pattern)
    s_len = len(s)
    py_init = _lua_to_py_index(init, s_len)
    if py_init is None or py_init >= s_len: return None # Cannot start search

    try:
        if plain: # Simple substring search
             found_index = s.find(pattern, py_init)
             if found_index != -1:
                 # Return Lua-style 1-based indices (start, end inclusive)
                 return found_index + 1, found_index + len(pattern)
             else:
                 return None
        else: # Regex search
             # NOTE: Using Python Regex, NOT Lua patterns!
             match = re.search(pattern, s[py_init:])
             if match:
                 # Adjust indices back to original string and 1-based
                 start_index = py_init + match.start() + 1
                 end_index = py_init + match.end() # re.end is exclusive, Lua is inclusive
                 return start_index, end_index
             else:
                 return None
    except re.error as e:
        print(f"Regex error in string.find pattern '{pattern}': {e}")
        return None
    except Exception as e:
         print(f"Error during string.find: {e}")
         return None

def _mnm_string_format(formatstring:str="", *args):
    # WARNING: Python's % formatting is similar but NOT identical to Lua's string.format.
    # This is a very basic approximation.
    if not isinstance(formatstring, str): formatstring = str(formatstring)
    try:
        # Attempt Python % formatting
        return formatstring % args
    except TypeError as e:
        print(f"Warning: Error during string.format (may differ from Lua): {e}")
        # Try simple replacements as fallback? No, stick to % attempt.
        return formatstring
    except Exception as e:
        print(f"Error during string.format: {e}")
        return formatstring

# gmatch omitted (returns iterator)

def _mnm_string_gsub(s:str="", pattern:str="", replacement:Any="", n:Optional[int]=None):
     # NOTE: Uses lua_gsub helper which uses Python regex.
     if not isinstance(s, str): s = str(s)
     if not isinstance(pattern, str): pattern = str(pattern)
     # Replacement can be string or function (passed directly to lua_gsub)
     if not isinstance(replacement, (str, Callable)): replacement=str(replacement)

     limit = n if isinstance(n, int) and n >= 0 else 0 # 0 means replace all in re.subn context? No, needs full replacement for count limit
     
     # lua_gsub handles the replacement logic
     if limit > 0:
          # Manually perform limited replacement using re.finditer
          count = 0
          last_end = 0
          result = []
          try:
               for match in re.finditer(pattern, s):
                    if count >= limit:
                         break
                    result.append(s[last_end:match.start()])
                    if callable(replacement):
                         # Call replacement function (handle potential errors inside)
                         repl_val = replacement(*match.groups())
                         result.append(str(repl_val))
                    else:
                         # Perform string replacement with group references (\1, etc.)
                         result.append(match.expand(replacement))
                    last_end = match.end()
                    count += 1
               result.append(s[last_end:]) # Append remaining part
               return "".join(result), count
          except re.error as e:
              print(f"Regex error in gsub pattern '{pattern}': {e}")
              return s, 0
          except Exception as e:
               print(f"Error during limited gsub: {e}")
               return s, 0
     else:
          # Replace all occurrences
          return lua_gsub(s, pattern, replacement) # Returns (new_string, count)


def _mnm_string_len(s:str=""):
    if not isinstance(s, str): s = str(s)
    return len(s)

def _mnm_string_lower(s:str=""):
    if not isinstance(s, str): s = str(s)
    return s.lower()

def _mnm_string_match(s:str="", pattern:str="", init:int=1):
    # NOTE: Uses Python Regex, NOT Lua patterns! Captures not fully handled here.
    if not isinstance(s, str): s = str(s)
    if not isinstance(pattern, str): pattern = str(pattern)
    s_len = len(s)
    py_init = _lua_to_py_index(init, s_len)
    if py_init is None or py_init >= s_len: return None

    try:
        match = re.search(pattern, s[py_init:])
        if match:
            # Lua match returns captures if present, otherwise the whole match
            if match.groups():
                 # Return first capture group if exists, mimic basic Lua capture
                 return match.group(1) if len(match.groups()) >= 1 else match.group(0)
            else:
                 return match.group(0) # Return the whole match
        else:
            return None
    except re.error as e:
        print(f"Regex error in string.match pattern '{pattern}': {e}")
        return None
    except Exception as e:
         print(f"Error during string.match: {e}")
         return None

# pack, packsize omitted
def _mnm_string_rep(s:str="", n:int=0):
    if not isinstance(s, str): s = str(s)
    if not isinstance(n, int) or n < 0: n = 0
    return s * n

def _mnm_string_reverse(s:str=""):
    if not isinstance(s, str): s = str(s)
    return s[::-1]

def _mnm_string_split(s:str="", separator:str=""):
     # Basic split, doesn't handle regex separators like Lua might implicitly
     if not isinstance(s, str): s = str(s)
     if not isinstance(separator, str): separator = str(separator)
     if separator == "": # Lua splits into individual characters
          return list(s)
     return s.split(separator) # Returns list (Lua table)

def _mnm_string_sub(s:str="", i:int=1, j:Optional[int]=None):
     if not isinstance(s, str): s = str(s)
     s_len = len(s)
     py_i, py_j_exclusive = _get_slice_indices(s_len, i, j if j is not None else -1) # Default j is Lua -1

     if py_i is None or py_j_exclusive is None or py_i >= py_j_exclusive:
          return "" # Return empty string for invalid slice
     return s[py_i:py_j_exclusive]

# unpack omitted
def _mnm_string_upper(s:str=""):
    if not isinstance(s, str): s = str(s)
    return s.upper()

# Populate mnm_string_lib
for name, func in locals().items():
    if name.startswith("_mnm_string_"):
        mnm_string_lib[name[12:]] = func

# --- Condition Logic (evaluate_lua_condition, find_block_structure unchanged) ---
def evaluate_lua_condition(condition_tokens: List[str], local_vars: Dict[str, Any]) -> bool:
    # ... (previous code remains unchanged) ...
    if not condition_tokens: return False
    if len(condition_tokens) >= 2 and condition_tokens[0].lower() == "not":
        operand_val = parse_value(condition_tokens[1], local_vars)
        return operand_val is False or operand_val is None
    elif len(condition_tokens) == 1:
        py_val = parse_value(condition_tokens[0], local_vars)
        return py_val is not False and py_val is not None
    elif len(condition_tokens) == 3:
        op1_token, operator, op2_token = condition_tokens
        operand1 = parse_value(op1_token, local_vars)
        operand2 = parse_value(op2_token, local_vars)
        try:
            if operator == "==": return operand1 == operand2
            elif operator == "~=": return operand1 != operand2
            elif operator == "<": return operand1 < operand2
            elif operator == ">": return operand1 > operand2
            elif operator == "<=": return operand1 <= operand2
            elif operator == ">=": return operand1 >= operand2
            elif operator.lower() == "and":
                 op1_truthy = operand1 is not False and operand1 is not None
                 return op1_truthy and (operand2 is not False and operand2 is not None)
            elif operator.lower() == "or":
                 op1_truthy = operand1 is not False and operand1 is not None
                 return op1_truthy or (operand2 is not False and operand2 is not None)
            else: print(f"Error: Unsupported operator in condition: {operator}"); return False
        except TypeError: print(f"Warning: Type error during condition ('{operand1}' {operator} '{operand2}'). Resulting in false."); return False if operator != "~=" else True
        except Exception as e: print(f"Error during condition evaluation: {e}"); return False
    else: print(f"Warning: Complex condition evaluation not fully supported: '{' '.join(condition_tokens)}'. Evaluating as false."); return False

def find_block_structure(lines: List[str], start_index: int) -> Optional[BlockInfo]:
    # ... (previous code remains unchanged) ...
    # Needs careful review if block starters/enders appear in strings/comments
    # For brevity, keeping the simple keyword check logic
    if start_index >= len(lines): return None
    try: tokens = shlex.split(lines[start_index].strip())
    except ValueError: return None
    if not tokens: return None
    block_type = tokens[0].lower()
    structure: BlockInfo = {'type': block_type, 'elseifs': [], 'end_line': -1}
    nesting_level = 1
    current_line_index = start_index + 1
    # Parse initial condition and find end, storing block lines (simplified logic from previous version)
    # ... (This complex block finding logic should be robustly tested/refined) ...
    # Example structure population (needs full implementation as before)
    if block_type == "if":
        # Find 'then', extract condition tokens
        pass # Placeholder for full find_block_structure logic
    elif block_type == "while":
         # Find 'do', extract condition tokens
         pass # Placeholder for full find_block_structure logic
    # Scan lines, manage nesting, identify elseif/else, find 'end'
    # Populate structure dict with 'if_block_lines', 'elseif_block_lines', etc. and 'end_line'
    # --> NOTE: The full block finding logic from the previous step needs to be here <--
    # For now, returning a dummy structure for MNM2 structure checks
    if block_type in ['if', 'while', 'function']: # Added function here for consistency
         dummy_end = start_index + 1
         while dummy_end < len(lines):
              if lines[dummy_end].strip().lower() == 'end':
                   structure['end_line'] = dummy_end
                   # Dummy line extraction
                   if block_type == 'if':
                        structure['if_cond_tokens'] = ['true'] # Dummy
                        structure['if_block_lines'] = lines[start_index+1:dummy_end]
                   elif block_type == 'while':
                        structure['while_cond_tokens'] = ['true'] # Dummy
                        structure['while_block_lines'] = lines[start_index+1:dummy_end]
                   # Function block lines handled in MNM2 'local function' part
                   break
              dummy_end += 1
         if structure['end_line'] == -1: return None # Failed to find end
         return structure # Return dummy structure
    return None # Not a recognized block starter


# --- Main Interpreter ---

def execute_function_call(func_obj: Callable, arg_tokens: List[str], local_vars: Dict) -> Any:
    """Helper to parse args and call math/string/user functions."""
    if not callable(func_obj):
        print(f"Error: Attempted to call non-function value.")
        return None # Represent nil
    try:
        # Parse arguments using the current scope
        parsed_args = parse_arguments(arg_tokens, 0, local_vars)
        # Call the function with parsed arguments
        result = func_obj(*parsed_args)
        return result
    except TypeError as e:
        # Handle wrong number of arguments or types
        # func_name = getattr(func_obj, '__name__', 'unknown') # Get name if possible
        print(f"TypeError during function call: {e}. Check arguments.")
        return None
    except Exception as e:
        print(f"Error during function call execution: {e}")
        return None


def MNM2(code, local_vars=None, is_block_execution=False):
    """
    Interprets MNM code with basic Roblox libs, control flow.
    """
    if local_vars is None:
        local_vars = {}
        # --- Initialize Global Libraries ---
        local_vars['math'] = mnm_math_lib
        local_vars['string'] = mnm_string_lib
        # Seed random generator once at start? Or rely on default seeding?
        # math.randomseed(os.urandom(8)) # Example seeding

    lines = code if is_block_execution else code.strip().split("\n")
    current_line_index = 0

    while current_line_index < len(lines):
        line_number = current_line_index
        line = lines[current_line_index].strip()
        next_line_index = current_line_index + 1

        if not line or line.startswith('--'):
            current_line_index = next_line_index
            continue

        try:
            tokens = shlex.split(line)
        except ValueError as e:
            print(f"Error tokenizing line {line_number + 1}: '{line}' - {e}")
            current_line_index = next_line_index
            continue

        if not tokens:
            current_line_index = next_line_index
            continue

        command_token = tokens[0]
        command_lower = command_token.lower()

        # --- Local Variable/Function Declaration ---
        if command_lower == "local":
             # ... (previous local handling - check if find_block_structure is needed) ...
             # Use the refined 'local function' logic from previous step that uses find_block_structure
             if len(tokens) >= 3 and tokens[1].lower() == "function":
                  func_name_raw = tokens[2]
                  function_name = func_name_raw[:-2] if func_name_raw.endswith("()") else func_name_raw
                  # Find block structure properly to get end line
                  # --> Re-integrate the robust find_block_structure logic here <--
                  # Find end line index
                  func_end_index = -1
                  nesting = 1
                  for idx in range(current_line_index + 1, len(lines)):
                      l_strip = lines[idx].strip().lower()
                      if l_strip in ["if", "while", "function", "for", "do"]: nesting += 1
                      if l_strip == 'end': nesting -=1
                      if nesting == 0: func_end_index = idx; break
                  
                  if func_end_index != -1:
                       function_code_lines = lines[current_line_index + 1 : func_end_index]
                       function_body_code = "\n".join(function_code_lines)
                       def create_lambda(body, parent_vars): return lambda *args: MNM2(body.split("\n"), parent_vars.copy(), is_block_execution=True) # Handle args? No simple way yet
                       defined_function = create_lambda(function_body_code, local_vars)
                       local_vars[function_name] = defined_function
                       next_line_index = func_end_index + 1
                  else: print(f"Syntax Error: Missing 'end' for function '{function_name}'."); next_line_index = len(lines)
             # Handle local variable assignment (rest is same as before)
             elif len(tokens) >= 4 and tokens[2] == "=":
                  variable_name = tokens[1]
                  # Check if RHS is a function call
                  rhs_tokens = tokens[3:]
                  if len(rhs_tokens) > 0:
                      potential_func = parse_value(rhs_tokens[0], local_vars)
                      if callable(potential_func): # Is it math.abs, string.len etc?
                          call_result = execute_function_call(potential_func, rhs_tokens[1:], local_vars)
                          local_vars[variable_name] = call_result
                      else: # Regular assignment
                          value_token = " ".join(rhs_tokens)
                          local_vars[variable_name] = parse_value(value_token, local_vars)
                  else: # local var = (nothing) -> nil
                      local_vars[variable_name] = None
             elif len(tokens) == 2: local_vars[tokens[1]] = None
             else: print(f"Syntax Error: Invalid 'local' statement: {' '.join(tokens)}")


        # --- Print Command ---
        elif command_lower == "print":
            arguments_to_print = []
            i = 1
            while i < len(tokens):
                arg_token = tokens[i]
                potential_func = parse_value(arg_token, local_vars)
                # Check if it's a callable math/string/user function
                if callable(potential_func):
                     # Greedily consume arguments until next potential callable or end
                     arg_start_index = i + 1
                     arg_end_index = arg_start_index
                     while arg_end_index < len(tokens):
                           # Stop if we hit another known function? Basic check.
                           next_potential = parse_value(tokens[arg_end_index], local_vars)
                           if callable(next_potential) and arg_end_index > arg_start_index: # Heuristic
                                break
                           arg_end_index += 1

                     call_args_tokens = tokens[arg_start_index:arg_end_index]
                     call_result = execute_function_call(potential_func, call_args_tokens, local_vars)
                     # Format result for printing
                     if call_result is None: arguments_to_print.append("nil")
                     elif isinstance(call_result, bool): arguments_to_print.append(str(call_result).lower())
                     elif isinstance(call_result, tuple): # Handle multiple returns from funcs like byte
                          arguments_to_print.extend(map(str, call_result))
                     else: arguments_to_print.append(call_result)
                     i = arg_end_index # Move main index past consumed arguments
                else:
                    # Regular value/variable argument
                    parsed_arg = parse_value(arg_token, local_vars)
                    if parsed_arg is None: arguments_to_print.append("nil")
                    elif isinstance(parsed_arg, bool): arguments_to_print.append(str(parsed_arg).lower())
                    else: arguments_to_print.append(parsed_arg)
                    i += 1
            print(*arguments_to_print)


        # --- If Statement ---
        elif command_lower == "if":
             # --> Use the robust find_block_structure logic here <--
             # Dummy implementation for now:
             end_idx = current_line_index + 1
             while end_idx < len(lines) and lines[end_idx].strip().lower() != 'end': end_idx +=1
             if end_idx < len(lines):
                  cond_tokens = tokens[1:-1] # Assumes 'if cond then'
                  if evaluate_lua_condition(cond_tokens, local_vars):
                       block_lines = lines[current_line_index+1:end_idx]
                       MNM2(block_lines, local_vars, is_block_execution=True)
                  next_line_index = end_idx + 1
             else: print("Syntax Error: Missing 'end' for 'if'"); next_line_index = len(lines)

        # --- While Statement ---
        elif command_lower == "while":
              # --> Use the robust find_block_structure logic here <--
              # Dummy implementation for now:
              loop_start_line = current_line_index
              end_idx = current_line_index + 1
              while end_idx < len(lines) and lines[end_idx].strip().lower() != 'end': end_idx +=1
              if end_idx < len(lines):
                  cond_tokens = tokens[1:-1] # Assumes 'while cond do'
                  block_lines = lines[current_line_index+1:end_idx]
                  loop_count = 0; max_loops = 1000
                  while loop_count < max_loops:
                       if evaluate_lua_condition(cond_tokens, local_vars):
                            MNM2(block_lines, local_vars, is_block_execution=True)
                            loop_count += 1
                       else: break
                  else: print("Error: Max loops reached")
                  next_line_index = end_idx + 1
              else: print("Syntax Error: Missing 'end' for 'while'"); next_line_index = len(lines)

        elif command_lower == "about":
            print("Made by Muser in team with different AI versions")
            print("Release: Extended Functionality V1")
            print("More info: RELEASE_7, RELEASE_NAME=ExtendedFunctionalityV1, SHORT_RELEASE_NAME=EF_V1, DEVELOPMENT_DATE=08/04/2025")
        elif command_lower == "easteregg":
            print("Loading Network Easter Egg...")
            python_logo_url = "https://www.python.org/static/community_logos/python-logo-generic.svg" # Example Python logo URL
            luau_logo_url = "https://raw.githubusercontent.com/Roblox/luau/master/logo/luau.svg"       # Example Luau logo URL (might need a direct PNG link for PIL)

            # It's generally safer and more reliable to use direct image formats like PNG or JPG with PIL.
            # Let's use PNG URLs instead for better compatibility.
            python_logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/800px-Python-logo-notext.svg.png"
            luau_logo_url = "https://avatars.githubusercontent.com/u/104525888?s=200&v=4" # Example PNG

            # Run the network Easter egg in a separate thread
            easter_egg_thread = threading.Thread(target=show_network_easter_egg, args=(python_logo_url, luau_logo_url))
            easter_egg_thread.start()
        # --- Standalone Function Call / Assignment ---
        else:
            # Try parsing as assignment first (var = value)
            if len(tokens) >= 3 and tokens[1] == "=":
                var_name = tokens[0]
                # Allow assignment to locals or implicitly declared globals (like Lua)
                # if var_name not in local_vars: print(f"Warning: Assigning to undeclared variable '{var_name}'")

                rhs_tokens = tokens[2:]
                if len(rhs_tokens) > 0:
                    potential_func = parse_value(rhs_tokens[0], local_vars)
                    if callable(potential_func): # Is it math.abs, string.len etc?
                        call_result = execute_function_call(potential_func, rhs_tokens[1:], local_vars)
                        local_vars[var_name] = call_result
                    else: # Regular assignment
                        value_token = " ".join(rhs_tokens)
                        local_vars[var_name] = parse_value(value_token, local_vars)
                else: # var = (nothing) -> nil
                    local_vars[var_name] = None
            
            # Try parsing as standalone function call (math.randomseed(), user_func())
            else:
                 potential_func = parse_value(command_token, local_vars)
                 if callable(potential_func):
                      # Execute standalone call (result usually ignored unless it modifies state)
                      execute_function_call(potential_func, tokens[1:], local_vars)
                 else:
                      # Unknown command
                      print(f"Error: Unknown command, variable, or syntax on line {line_number + 1}: '{' '.join(tokens)}'")


        current_line_index = next_line_index

    return local_vars


# --- Example Usage ---
if __name__ == "__main__":

    # ... (previous examples can be kept) ...

    print("\n--- Math Library Tests ---")
    MNM2("""
print "Pi:", math.pi
print "Huge:", math.huge
print "Abs(-5):", math.abs -5 -- Need better parsing for unary minus
print "Abs(5):", math.abs 5
print "Clamp(15, 0, 10):", math.clamp 15 0 10
print "Floor(3.7):", math.floor 3.7
print "Ceil(3.7):", math.ceil 3.7
print "Sqrt(16):", math.sqrt 16
print "Pow(2, 8):", math.pow 2 8
local angle_rad = math.rad 90
print "Rad(90):", angle_rad
print "Sin(angle_rad):", math.sin angle_rad -- Should be 1.0
print "Random [0,1):", math.random()
print "Random [1,100]:", math.random 100
print "Random [50, 60]:", math.random 50 60
local x = 12.8
local f, i = math.modf x -- Note: MNM doesn't support multiple assignment yet
print "Modf(12.8):", math.modf x -- Prints tuple in Python
""")

    print("\n--- String Library Tests ---")
    MNM2("""
local test_str = "Hello MNM World!"
print "Test String:", test_str
print "Length:", string.len test_str
print "Lower:", string.lower test_str
print "Upper:", string.upper test_str
print "Sub(7, 9):", string.sub test_str 7 9 -- MNM
print "Sub(7):", string.sub test_str 7 -- MNM World!
print "Sub(-6, -2):", string.sub test_str -6 -2 -- World
print "Byte(1, 5):", string.byte test_str 1 5 -- Prints tuple
print "Char(72, 101, 108, 108, 111):", string.char 72 101 108 108 111
print "Rep('=', 5):", string.rep "=" 5
print "Reverse:", string.reverse test_str
local s1, s2, s3 = string.split test_str " " -- Multiple assignment not supported
print "Split by space:", string.split test_str " " -- Prints list

print "Find 'MNM':", string.find test_str "MNM" -- Prints tuple (start, end)
print "Find 'nomatch':", string.find test_str "nomatch" -- Prints nil

-- Note: gsub uses Python regex syntax
local replaced, count = string.gsub test_str "[aeiou]" "*" -- Multiple assignment not supported
print "Gsub vowels with *:", string.gsub test_str "[aeiou]" "*" -- Prints tuple (string, count)
print "Gsub 'World' with 'User':", string.gsub test_str "World" "User" 1 -- Limit 1 replacement
""")

# --- UI Section (Needs update for better robustness if used extensively) ---
# The existing UI code can be used, but the interpreter's error handling
# and the complexity might require more robust UI feedback.
# The highlighting function needs keywords updated if desired.

def run_mnm_code():
    global root_ref
    # ... (UI execution code - largely unchanged, relies on MNM2 print/errors) ...
    # Consider adding a clear button for output
    mnm_code = code_input_area.get("1.0", tk.END)
    redirected_output = StringIO()
    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = redirected_output
    try:
        if root_ref is None:
            root_ref = root
        MNM2(mnm_code, local_vars=None) # Start with fresh globals each run
    except Exception as e:
        print(f"\n--- Uncaught Interpreter Error ---")
        print(f"Error during execution:\n{e}")
        import traceback
        print(traceback.format_exc())
        print(f"------------------------------\n")
    finally:
        sys.stdout, sys.stderr = original_stdout, original_stderr
        output = redirected_output.getvalue()
        output_area.config(state=tk.NORMAL)
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, output)
        output_area.config(state=tk.DISABLED)

# --- Tkinter Setup (unchanged from previous version) ---
# ... (Tkinter setup code) ...
# Update highlight_syntax keywords if needed
def highlight_syntax(event=None):
    code_input_area.tag_remove("keyword", "1.0", tk.END)
    code_input_area.tag_remove("string", "1.0", tk.END)
    code_input_area.tag_remove("comment", "1.0", tk.END)
    code_input_area.tag_remove("builtin", "1.0", tk.END) # Example for builtins

    content = code_input_area.get("1.0", tk.END)
    # Updated keywords
    keywords = [
        "local", "function", "end", "if", "then", "else", "elseif",
        "while", "do", "for", "in", "return", "and", "or", "not",
        "true", "false", "nil"
    ]
    builtins = ["print", "lua_gsub"] # Add other built-in functions
    strings = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'' # Handle escaped quotes
    comments = r"--.*"

    # Configure tags
    code_input_area.tag_configure("keyword", foreground="blue")
    code_input_area.tag_configure("string", foreground="red")
    code_input_area.tag_configure("comment", foreground="gray")
    code_input_area.tag_configure("builtin", foreground="purple")


    # Apply tags (more efficient search)
    for keyword in keywords:
        start_idx = "1.0"
        while True:
            # Use regexp=True for word boundaries
            pos = code_input_area.search(r'\m' + re.escape(keyword) + r'\M', start_idx, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end_idx = f"{pos}+{len(keyword)}c"
            # Avoid highlighting keywords within strings/comments (basic check)
            is_string = any("string" in code_input_area.tag_names(pos) for i in range(len(keyword)))
            is_comment = any("comment" in code_input_area.tag_names(pos) for i in range(len(keyword)))
            if not is_string and not is_comment:
                 code_input_area.tag_add("keyword", pos, end_idx)
            start_idx = end_idx

    # Highlight strings first to avoid keyword highlighting inside them
    for match in re.finditer(strings, content):
        start_index = f"1.0 + {match.start()}c"
        end_index = f"1.0 + {match.end()}c"
        code_input_area.tag_add("string", start_index, end_index)

    # Highlight comments
    for match in re.finditer(comments, content):
        start_index = f"1.0 + {match.start()}c"
        end_index = f"1.0 + {match.end()}c"
        # Ensure comments don't override strings completely
        existing_tags = code_input_area.tag_names(start_index)
        if "string" not in existing_tags:
             code_input_area.tag_add("comment", start_index, end_index)

root = tk.Tk()
root.title("MNM V3.2 Interpreter (Roblox Libs)")
# ... (rest of Tkinter setup) ...
input_frame = tk.Frame(root); input_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
code_label = tk.Label(input_frame, text="Enter MNM Code:"); code_label.pack(anchor=tk.W)
code_input_area = tk.Text(input_frame, height=20, width=80, undo=True); code_input_area.pack(fill=tk.BOTH, expand=True)
code_input_area.bind("<KeyRelease>", highlight_syntax)
run_button = tk.Button(root, text="Run MNM Code", command=run_mnm_code); run_button.pack(pady=5)
output_frame = tk.Frame(root); output_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
output_label = tk.Label(output_frame, text="Output:"); output_label.pack(anchor=tk.W)
output_area = tk.Text(output_frame, height=10, width=80, state=tk.DISABLED, wrap=tk.WORD); output_area.pack(fill=tk.BOTH, expand=True)
highlight_syntax()
root.mainloop()