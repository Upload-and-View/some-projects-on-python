import re, shlex
from colorama import Fore, Style, Back, init
import math
import time
import random
import copy # Might be needed later if tables are added
import traceback

variables = {}
builtins = {} # Dictionary for built-in functions

init(autoreset=True)
debug_mode = False # Default to False unless needed
muser_print_allowwed = False # Keep user setting

# --- Output Functions ---
def muser_print(*args):
    if muser_print_allowwed:
        print(f"{Back.WHITE}{Fore.YELLOW}{Style.BRIGHT}[MUSER]: {Style.RESET_ALL}{Fore.GREEN}{Back.WHITE}" + "".join(map(str, args)) + f"{Style.RESET_ALL}")

def muser_debug_print(*args):
    if debug_mode:
        print(f"{Back.WHITE}{Fore.GREEN}{Style.BRIGHT}[DEBUG]: {Style.RESET_ALL}{Fore.GREEN}{Back.WHITE}" + "".join(map(str, args)) + f"{Style.RESET_ALL}")

def muser_output_print(*args):
     print(f"{Back.WHITE}{Style.BRIGHT}[OUTPUT]: {Style.RESET_ALL}{Back.WHITE}{Fore.BLACK}" + "".join(map(str, args)) + f"{Style.RESET_ALL}")

def muser_error_print(*args):
     print(f"{Back.WHITE}{Fore.RED}{Style.BRIGHT}[ERROR]: {Style.RESET_ALL}{Fore.RED}{Back.WHITE}" + "".join(map(str, args)) + f"{Style.RESET_ALL}")

# --- Built-in Function Implementations (Keep from previous version) ---
def _convert_to_num(val):
    if isinstance(val, (int, float)): return val
    try: return int(val)
    except (ValueError, TypeError):
        try: return float(val)
        except (ValueError, TypeError): return None

# ... (Keep all _builtin_sqrt, _builtin_pow, ..., _builtin_tostring definitions) ...
def _builtin_sqrt(x=None):
    num_x = _convert_to_num(x)
    if num_x is None or num_x < 0: muser_error_print("sqrt requires a non-negative number."); return None
    return math.sqrt(num_x)
def _builtin_pow(base=None, exp=None):
    num_base = _convert_to_num(base); num_exp = _convert_to_num(exp)
    if num_base is None or num_exp is None: muser_error_print("pow requires two numbers."); return None
    return math.pow(num_base, num_exp)
def _builtin_random(a=None, b=None):
    num_a = _convert_to_num(a); num_b = _convert_to_num(b)
    if num_a is None and num_b is None: return random.random()
    elif num_b is None:
        if num_a is None or num_a <= 0: muser_error_print("random(max): max must be > 0."); return None
        return random.randint(1, int(num_a))
    else:
        if num_a is None or num_b is None: muser_error_print("random(min,max): requires two numbers."); return None
        if num_a > num_b: muser_error_print("random(min,max): min cannot be greater than max."); return None
        return random.randint(int(num_a), int(num_b))
def _builtin_len(s=None): return len(str(s)) if s is not None else 0
def _builtin_upper(s=None): return str(s).upper() if s is not None else ""
def _builtin_lower(s=None): return str(s).lower() if s is not None else ""
def _builtin_sub(s=None, i=None, j=None):
    s_str = str(s) if s is not None else ""; s_len = len(s_str)
    num_i = _convert_to_num(i)
    if num_i is None: muser_error_print("sub: index i must be number."); return ""
    py_i = int(num_i) - 1 if num_i > 0 else s_len + int(num_i)
    py_j_exclusive = s_len
    if j is not None:
        num_j = _convert_to_num(j)
        if num_j is None: muser_error_print("sub: index j must be number."); return ""
        py_j = int(num_j) - 1 if num_j > 0 else s_len + int(num_j)
        py_j_exclusive = py_j + 1
    if py_i < 0: py_i = 0
    if py_j_exclusive > s_len: py_j_exclusive = s_len
    if py_i >= py_j_exclusive: return ""
    return s_str[py_i:py_j_exclusive]
def _builtin_clock(): return time.perf_counter()
def _builtin_time(): return time.time()
def _builtin_type(val=None):
    if val is None: return "nil"
    py_type = type(val)
    if py_type is str: return "string"
    if py_type in (int, float): return "number"
    if py_type is bool: return "boolean"
    if py_type is list: return "table"
    if py_type is dict: return "table"
    if callable(val): return "function"
    return "userdata"
def _builtin_tostring(val=None):
    if val is None: return "nil"
    if val is True: return "true"
    if val is False: return "false"
    return str(val)

# --- Populate builtins dictionary ---
builtins['sqrt'] = _builtin_sqrt
builtins['pow'] = _builtin_pow
builtins['random'] = _builtin_random
builtins['len'] = _builtin_len
builtins['upper'] = _builtin_upper
builtins['lower'] = _builtin_lower
builtins['sub'] = _builtin_sub
builtins['clock'] = _builtin_clock
builtins['time'] = _builtin_time
builtins['type'] = _builtin_type
builtins['tostring'] = _builtin_tostring
builtins['pi'] = math.pi # Constant value
# Expose muser_print
builtins['muser_print'] = muser_print # Add the python function directly
# --- End Built-ins ---


def evaluate_expression(expression_tokens):
    """
    Evaluates simple expressions from a list of tokens.
    Handles: Literals, Variables, Constants(pi), Built-in calls, Basic Arithmetic/Comparison.
    Limitation: No operator precedence, no parentheses, left-to-right for single op.
    """
    if not expression_tokens:
        return None

    muser_debug_print(f" Evaluating expression tokens: {expression_tokens}")

    # --- Function Call Check ---
    # Handle zero-arg calls like clock() or just clock
    raw_func_name = expression_tokens[0]
    func_name = raw_func_name[:-2] if raw_func_name.endswith('()') else raw_func_name
    func_name = func_name.lower() # Look up builtins case-insensitively

    if func_name in builtins and callable(builtins[func_name]):
        func = builtins[func_name]
        # Evaluate arguments recursively (handles single-token args well)
        arg_values = [evaluate_expression([arg]) for arg in expression_tokens[1:]]
        muser_debug_print(f"  Calling built-in '{func_name}' with args: {arg_values}")
        try:
            return func(*arg_values)
        except TypeError as e:
             muser_error_print(f"  Wrong arguments for function '{func_name}': {e}")
             return None
        except Exception as e:
             muser_error_print(f"  Error executing function '{func_name}': {e}")
             return None

    # --- Single Token Evaluation (Base cases) ---
    if len(expression_tokens) == 1:
        token = expression_tokens[0]
        # Strip () if it's the only token, e.g., evaluate_expression(['clock()'])
        if token.endswith('()'):
             token = token[:-2]
        token_lower = token.lower()

        if token_lower == "true": return True
        if token_lower == "false": return False
        if token_lower == "nil" or token_lower == "none": return None
        if token in variables: return variables[token]
        if token_lower in builtins and not callable(builtins[token_lower]): # Check constants like pi
             return builtins[token_lower]

        # Try converting to number
        num_val = _convert_to_num(token)
        if num_val is not None: return num_val

        # Fallback: string literal or unknown variable (return as string)
        muser_debug_print(f"  Single token '{token}' evaluated as string (or unknown var).")
        return token

    # --- Simple Arithmetic (+, -, *, /) ---
    if len(expression_tokens) == 3 and expression_tokens[1] in ['+', '-', '*', '/']:
        left_val = evaluate_expression([expression_tokens[0]]) # Evaluate left operand
        right_val = evaluate_expression([expression_tokens[2]]) # Evaluate right operand
        op = expression_tokens[1]
        muser_debug_print(f"  Arithmetic: {left_val} {op} {right_val}")

        num_left = _convert_to_num(left_val)
        num_right = _convert_to_num(right_val)

        if num_left is None or num_right is None:
            muser_error_print(f"  Arithmetic requires numbers, got '{left_val}' ({type(left_val)}) and '{right_val}' ({type(right_val)}).")
            return None
        try:
            if op == '+': return num_left + num_right
            if op == '-': return num_left - num_right
            if op == '*': return num_left * num_right
            if op == '/':
                if num_right == 0: muser_error_print("  Division by zero."); return None
                return num_left / num_right # Float division
        except Exception as e:
            muser_error_print(f"  Error during arithmetic {num_left} {op} {num_right}: {e}")
            return None

    # --- Simple Comparison (==, ~=, !=, <, >, <=, >=) ---
    if len(expression_tokens) == 3 and expression_tokens[1] in ['==', '~=', '!=', '<', '>', '<=', '>=']:
        left = evaluate_expression([expression_tokens[0]])
        right = evaluate_expression([expression_tokens[2]])
        op = expression_tokens[1]
        muser_debug_print(f"  Comparison: {left} {op} {right}")

        if op == '~=': op = '!=' # Treat ~= as !=

        try:
            if op == '==': return left == right
            if op == '!=': return left != right
            # Numeric comparisons need numbers for remaining ops
            num_left = _convert_to_num(left)
            num_right = _convert_to_num(right)
            if num_left is None or num_right is None:
                 # Comparing non-numbers with <, >, etc. is generally false
                 muser_debug_print(f"  Comparison '{op}' requires numbers, got '{left}' and '{right}'. Result: false.")
                 return False
            if op == '<': return num_left < num_right
            if op == '>': return num_left > num_right
            if op == '<=': return num_left <= num_right
            if op == '>=': return num_left >= num_right
        except Exception as e: # Catch potential TypeErrors during comparison
            muser_error_print(f"  Type error during comparison {left} {op} {right}: {e}")
            return False # Comparing incompatible types is false

    # --- Fallback ---
    # If it's not a single value, function call, arithmetic, or comparison,
    # treat the whole thing as an unevaluated string for now.
    result = " ".join(expression_tokens)
    muser_debug_print(f"  Expression '{result}' evaluated as string (fallback).")
    return result


# --- Interpreter and Parser ---

def interpreter(tokens, line_number=None):
    """Interprets a single command token list."""
    global variables
    if not tokens:
        return  # Skip empty lines/tokens

    # Filter out comment tokens
    active_tokens = [token for token in tokens if not token.startswith("#")]

    if not active_tokens:
        return  # Treat lines with only comments as empty

    command = active_tokens[0].lower()
    args = active_tokens[1:]

    muser_debug_print(f"Interpreting: Command='{command}', Args={args} (Line: {line_number})")

    if command == "print":
        filtered_args = []
        for arg in args:
            if "#" in arg:
                arg_parts = arg.split("#", 1)
                if arg_parts[0]:
                    filtered_args.append(arg_parts[0].strip())
                break
            else:
                filtered_args.append(arg)

        output_parts = []
        i = 0
        while i < len(filtered_args):
            expr_tokens = []
            while i < len(filtered_args):
                expr_tokens.append(filtered_args[i])
                if len(expr_tokens) > 0 and i + 1 < len(filtered_args) and filtered_args[i + 1] not in ['+', '-', '*', '/', '==', '~=', '!=', '<', '>', '<=', '>=']:
                    try:
                        evaluated = evaluate_expression(expr_tokens)
                        if evaluated is not None:
                            output_parts.append(_builtin_tostring(evaluated))
                            i += 1
                            break
                    except Exception as e:
                        muser_error_print(f"Error evaluating expression '{' '.join(expr_tokens)}' on line {line_number} (within print): {e}")
                        output_parts.append(f"[Error: {e}]")  # Output error in the print
                        i += 1
                        break
                i += 1
            else:
                if expr_tokens:
                    try:
                        output_parts.append(_builtin_tostring(evaluate_expression(expr_tokens)))
                    except Exception as e:
                        muser_error_print(f"Error evaluating expression '{' '.join(expr_tokens)}' on line {line_number} (within print): {e}")
                        output_parts.append(f"[Error: {e}]")
        muser_output_print(" ".join(output_parts))
        # --- End of Print ---

    elif command == "let":
        filtered_args = []
        for arg in args:
            if "#" in arg:
                arg_parts = arg.split("#", 1)
                if arg_parts[0]:
                    filtered_args.append(arg_parts[0].strip())
                break
            else:
                filtered_args.append(arg)

        if len(filtered_args) >= 3 and filtered_args[1] == "=":
            variable_name = filtered_args[0]
            value_tokens = filtered_args[2:]
            try:
                variable_value = evaluate_expression(value_tokens)
                variables[variable_name] = variable_value
                muser_debug_print(f"Variable Set: {variable_name} = {variable_value} ({type(variable_value)}) (Line: {line_number})")
            except Exception as e:
                muser_error_print(f"Error evaluating expression for 'let {variable_name}' on line {line_number} (within let): {e}")
        elif len(filtered_args) == 1 and filtered_args[0].endswith('='):
            variable_name = filtered_args[0][:-1].strip()
            if variable_name:
                variables[variable_name] = None
                muser_debug_print(f"Variable Set: {variable_name} = None (Line: {line_number})")
            else:
                muser_error_print(f"Syntax error: Invalid 'let' statement on line {line_number}: {' '.join(tokens)}")
        elif len(filtered_args) == 2 and filtered_args[1] == '=':
            variables[filtered_args[0]] = None
            muser_debug_print(f"Variable Set: {filtered_args[0]} = None (Line: {line_number})")
        else:
            muser_error_print(f"Syntax error: Invalid 'let' statement on line {line_number}: {' '.join(tokens)}")

    elif command == "loop":
        if len(args) >= 2 and args[-1].lower() == "do":
            count_tokens = args[:-1]  # Everything before 'do' is the count expression
            evaluated_count = evaluate_expression(count_tokens)

            if not isinstance(evaluated_count, (int, float)):
                muser_error_print(f"Error: Loop count must be a number on line {line_number}.")
                return

            integer_count = int(evaluated_count)

            if integer_count < 0:
                muser_debug_print(f"Someone used loop on line {line_number} with negative integer {integer_count}, not looping =)")
                return
            elif integer_count == 0:
                muser_debug_print(f"Someone used loop on line {line_number} with integer 0, not looping =)")
                return
            elif integer_count == 1:
                muser_debug_print(f"Hey, you have {integer_count} iteration on line {line_number}, why not using the code directly without a loop?")
                # --- Retrieve and execute the loop body once ---
                loop_body_tokens_list = args[:-2]
                if isinstance(loop_body_tokens_list, list):
                    muser_debug_print(f"Executing loop body once.")
                    for body_token_list in loop_body_tokens_list:
                        interpreter(body_token_list, line_number)
                # --- End of single execution ---
            else:
                # --- Retrieve and execute the loop body multiple times ---
                loop_body_tokens_list = args[:-2]
                if isinstance(loop_body_tokens_list, list):
                    muser_debug_print(f"Someone used loop on line {line_number} with integer {integer_count}, looping {integer_count} times.")
                    for _ in range(integer_count):
                        for body_token_list in loop_body_tokens_list:
                            interpreter(body_token_list, line_number)
                # --- End of loop execution ---
        else:
            muser_error_print(f"Syntax error: Invalid 'loop' statement on line {line_number}. Expected 'loop <count> do'.")

    # Check for built-in function calls AS commands (side effects, ignore result)
    elif command in builtins:
        func = builtins[command]
        if callable(func):
            filtered_args_func = []
            for arg in args:
                if "#" in arg:
                    arg_parts = arg.split("#", 1)
                    if arg_parts[0]:
                        filtered_args_func.append(arg_parts[0].strip())
                    break
                else:
                    filtered_args_func.append(arg)
            arg_values = [evaluate_expression([arg]) for arg in filtered_args_func]  # Eval each arg token individually
            muser_debug_print(f" Calling standalone built-in '{command}' with arg values: {arg_values} (Line: {line_number})")
            try:
                func(*arg_values)  # Execute, ignore result
            except TypeError as e:
                muser_error_print(f" Wrong arguments for function '{command}' on line {line_number} (standalone call): {e}")
            except Exception as e:
                muser_error_print(f" Error executing function '{command}' on line {line_number} (standalone call): {e}")
        else:
            # Accessing a constant like 'pi' as a command makes no sense
            muser_error_print(f"Cannot execute non-function built-in '{command}' as a command on line {line_number}.")

    elif command in ["if", "else", "end", "then"]:
        pass  # Handled by parser
    else:
        muser_error_print(f"Unknown command: {tokens[0]} on line {line_number}")


def parser(code):
    """Parses and executes the code line by line, handling simple blocks."""
    muser_print("Parser Started.")
    lines = code.strip().splitlines()
    i = 0
    while i < len(lines):
        line_number = i + 1
        line = lines[i].strip()
        muser_debug_print(f"Parsing Line {line_number}: '{line}'")

        if not line or line.startswith("#"):
            i += 1
            continue

        try:
            tokens = shlex.split(line)
        except ValueError as e:
            muser_error_print(f"Tokenization error on line {line_number}: {e}")
            i += 1
            continue
        if not tokens:
            i += 1
            continue

        command = tokens[0].lower()

        try:  # Add error handling around processing each line/block
            if command == "if":
                # --- Refined If/Else Block Handling ---
                if len(tokens) >= 3 and tokens[-1].lower() == "then":
                    condition_tokens = tokens[1:-1]
                    muser_debug_print(f" IF condition tokens: {condition_tokens}")
                    condition_value = evaluate_expression(condition_tokens)
                    muser_debug_print(f" IF condition value: {condition_value}")

                    then_block_lines = []
                    else_block_lines = []
                    current_block = then_block_lines
                    block_level = 1
                    if_start_line = line_number
                    j = i + 1
                    found_end = False
                    while j < len(lines):
                        block_line = lines[j]
                        block_line_strip = block_line.strip()
                        block_tokens = []
                        if block_line_strip:
                            try:
                                block_tokens = shlex.split(block_line_strip)
                            except ValueError as e:
                                muser_error_print(f"Tokenization error within IF block on line {j + 1}: {e}")
                                pass

                        block_command = block_tokens[0].lower() if block_tokens else ""
                        muser_debug_print(f"  Scanning L{j + 1}: '{block_line_strip}' -> Cmd='{block_command}', Level={block_level}")

                        if block_command == "if":
                            block_level += 1
                        elif block_command == "else" and block_level == 1:
                            current_block = else_block_lines
                        elif block_command == "end":
                            block_level -= 1
                            if block_level == 0:
                                found_end = True
                                break

                        # Add line to the correct block (unless it's the 'else'/'end' keyword itself at level 1)
                        if not (block_level == 0 or (block_level == 1 and block_command in ["else", "end"])):
                            current_block.append(block_line)
                        j += 1

                    if not found_end:
                        muser_error_print(f"Syntax Error: Missing 'end' for 'if' block starting on line {if_start_line}.")
                        i = len(lines)  # Stop parsing
                    else:
                        muser_debug_print(f" IF block found: THEN lines={len(then_block_lines)}, ELSE lines={len(else_block_lines)}, Ends line {j + 1}")
                        if condition_value:
                            muser_debug_print("Executing THEN block...")
                            parser("\n".join(then_block_lines))  # Recursive call
                        elif else_block_lines:
                            muser_debug_print("Executing ELSE block...")
                            parser("\n".join(else_block_lines))  # Recursive call
                        i = j  # Move main index past the 'end' line
                else:
                    muser_error_print(f"Syntax error: Invalid 'if' statement on line {line_number}: '{line}'")
                    i += 1
                # --- End of If/Else Handling ---
            elif command == "loop":
                if len(tokens) >= 2 and tokens[-1].lower() == "do":
                    count_tokens = tokens[1:-1]
                    try:
                        evaluated_count = evaluate_expression(count_tokens)
                        if not isinstance(evaluated_count, (int, float)):
                            muser_error_print(f"Error: Loop count must be a number on line {line_number}.")
                        else:
                            integer_count = int(evaluated_count)
                            if integer_count < 0:
                                muser_debug_print(f"Someone used loop on line {line_number} with negative integer {integer_count}, not looping =)")
                            elif integer_count == 0:
                                muser_debug_print(f"Someone used loop on line {line_number} with integer 0, not looping =)")
                            elif integer_count == 1:
                                muser_debug_print(f"Hey, you have {integer_count} iteration on line {line_number}, why not using the code directly without a loop?")
                                # Execute the next lines directly
                                k = i + 1
                                while k < len(lines) and lines[k].strip().lower() != "end":
                                    parser(lines[k])
                                    k += 1
                                i = k # Move past the 'end'
                            elif integer_count > 1:
                                muser_debug_print(f"Someone used loop on line {line_number} with integer {integer_count}, preparing to loop.")
                                loop_body_lines = []
                                loop_start_line = line_number
                                k = i + 1
                                end_found = False
                                while k < len(lines):
                                    body_line = lines[k]
                                    if body_line.strip().lower() == "end":
                                        end_found = True
                                        break
                                    loop_body_lines.append(body_line)
                                    k += 1

                                if not end_found:
                                    muser_error_print(f"Syntax Error: Missing 'end' for 'loop' on line {loop_start_line}.")
                                else:
                                    muser_debug_print(f"Loop body found, executing {integer_count} times.")
                                    for _ in range(integer_count):
                                        muser_debug_print(f"--- Loop Iteration {_ + 1} (starting at line {loop_start_line + 1}) ---")
                                        parser("\n".join(loop_body_lines)) # Recursive call for the loop body
                                    i = k # Move past the 'end'
                            else:
                                    i += 1 # Move to the next line if 'end' is missing
                    except Exception as e:
                        muser_error_print(f"Error evaluating loop count on line {line_number}: {e}")
                        i += 1
                else:
                    muser_error_print(f"Syntax error: Invalid 'loop' statement on line {line_number}. Expected 'loop <count> do'.")
                    i += 1
            else:
                interpreter(tokens, line_number)  # Handle other commands
                i += 1
        except Exception as e:
            muser_error_print(f"--- Runtime Error on line {line_number} ---")
            muser_error_print(f"Line: '{line}'")
            muser_error_print(f"Error: {e}")
            traceback.print_exc()
            i += 1  # Move to next line after error

    muser_print("Parser Finished.")


if __name__ == "__main__":
    code_example = """
    # This is a comment
    muser_print Welcome to MuserLang!

    let x = 10
    let y = 5.5
    let name = "Muser"

    print Values: x name y

    # Basic math
    let sum = x + y
    print Sum: sum
    let product = x * 2
    print Product: product
    let power = pow 2 8
    print Power: power
    let root = sqrt 16
    print Root: root
    print Random default: random() # Zero arg call test
    print Random max 10: random 10 # Single arg
    print Random 50 to 60: random 50 60 # Two args

    # Basic strings
    print Name upper: upper name
    print Name lower: lower name
    print Name length: len name
    print Substring: sub name 2 4 # use

    # OS time
    let start = clock()
    print Start clock: start
    # some delay? Need loops first for noticeable diff
    let end_ = clock()
    print End clock: end_
    # Arithmetic with variables holding numbers
    let elapsed = end_ - start
    print Elapsed: elapsed

    # Type checking
    print Type of x: type x
    print Type of name: type name
    print Type of nil_var: type nil_var # Unknown var -> string
    let z = nil
    print Type of z: type z # nil
    print Type of true: type true
    print Type of sqrt: type sqrt # function


    # Conditional logic
    print --- Conditionals ---
    if x > 5 then
      print x is greater than 5
      let inner_var = "Inside if"
      print inner_var
    else
      print x is not greater than 5
    end

    if name == "Muser" then
      print Hello Muser!
    end

    let check = false
    if check then
      print Check is true # Won't print
    else
      print Check is false
    end
    print ---Others---
    loop 10 do
    print "Looped 10 times"
    end
    if 10 >= 10 then
       print 10 is >= 10
    end

    # Error case: Unknown command
    unknown_command arg1

    # Error case: Invalid let
    let =

    # Error case: Arithmetic with incompatible type
    # print name + 5
    """
    # Execute the code
    parser(code_example)

    # Print final variable state
    print("\n--- Final Variables ---")
    for var_name, var_value in variables.items():
        # Use tostring for consistent output formatting
        print(f" {var_name} ({_builtin_type(var_value)}) = {_builtin_tostring(var_value)}")
    print("---------------------")