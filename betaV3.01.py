# PLua (Lua to Python) - MNM (Muser Not Matters) v3
# Updated by Muser (New Big Update (NBU))
import re
import shlex # Use shlex for better tokenization respecting quotes
from typing import Any
import tkinter as tk # Use tkinter to run the syntax highlighted edition
# --- Utility Functions ---

def lua_gsub(text, pattern, replacement):
    """
    Mimics Lua's string.gsub function.
    """
    count = 0
    if callable(replacement):
        def replace_func(match):
            nonlocal count
            count += 1
            # Lua replacement function receives capture groups as arguments
            # Python re passes the match object. We pass the groups.
            return replacement(*match.groups()) # Pass groups to mimic Lua
        modified_text = re.sub(pattern, replace_func, text)
        # Note: Calculating count correctly with callable replacement in re.sub
        # requires iterating or a different approach if the replacement function
        # itself doesn't always perform a replacement. For simplicity,
        # assuming the provided function *always* replaces if called.
        # A more accurate count might require re.finditer if complex logic needed.
        # We'll stick to incrementing within the wrapper for now.
    else:
        # re.subn returns a tuple (new_string, number_of_subs_made)
        modified_text, count = re.subn(pattern, replacement, text)
    return modified_text, count

def convertsimplevalues(val: str) -> Any:
    """Converts string representation of simple Lua values to Python types."""
    if not isinstance(val, str): # If already converted, return as is
        return val
    
    lower_val = val.lower()
    if lower_val == "nil":
        return None
    elif lower_val == "false":
        return False
    elif lower_val == "true":
        return True

    # Handle Strings (already stripped by parse_value if needed)
    if val.startswith('"') and val.endswith('"'):
         return val[1:-1]
    if val.startswith("'") and val.endswith("'"): # Allow single quotes too
         return val[1:-1]

    # Handle Numbers
    try:
        return int(val)
    except ValueError:
        try:
            # Improved float check: handle potential signs and ensure it's numeric
            if val.replace('.', '', 1).replace('-', '', 1).isdigit():
                 return float(val)
            else:
                 # Not a simple value we recognize - return original string
                 # This might represent a variable name or complex type later
                 return val
        except ValueError:
            # If it's not a simple type, return it as is (likely variable name)
            return val

def parse_value(token: str, local_vars: dict) -> Any:
    """Parses a token into a Python value, checking variables first."""
    # 1. Check if it's a known variable
    if token in local_vars:
        return local_vars[token]
    
    # 2. Check if it's a simple literal value (string, number, bool, nil)
    return convertsimplevalues(token)

# --- Condition Logic (Present but not used by MNM2 yet) ---
# Note: This logic is complex and might need revision if implementing 'if'.
# It currently doesn't handle operator precedence well for complex expressions.

def convertcondition(val: str) -> bool:
    """Attempts to evaluate a simple Lua-like condition string."""
    parts = val.split() # Basic split, might fail on complex cases
    if not parts:
        return True  # Empty condition is often true? (Consider Lua's truthiness)

    # --- Simple Case: Single Value (Lua Truthiness) ---
    if len(parts) == 1:
        py_val = convertsimplevalues(parts[0])
        # Lua truthiness: false and nil are false, everything else is true
        return py_val is not False and py_val is not None

    # --- Binary Operation ---
    if len(parts) == 3:
        operand1_lua = parts[0]
        operator_lua = parts[1]
        operand2_lua = parts[2]

        # NOTE: This assumes operands are simple values, not complex expressions or variables
        operand1_python = convertsimplevalues(operand1_lua)
        operand2_python = convertsimplevalues(operand2_lua)

        # Comparison Operators
        if operator_lua == "==":
            return operand1_python == operand2_python
        elif operator_lua == "~=": # Lua not equal
            return operand1_python != operand2_python
        elif operator_lua == "<":
            return operand1_python < operand2_python
        elif operator_lua == ">":
            return operand1_python > operand2_python
        elif operator_lua == "<=":
            return operand1_python <= operand2_python
        elif operator_lua == ">=":
            return operand1_python >= operand2_python
        # Logical Operators (Basic) - Doesn't handle precedence correctly here
        elif operator_lua == "and":
             # Python 'and' short-circuits like Lua 'and' but returns True/False
             # Lua 'and' returns the first operand if falsy, otherwise the second
             op1_truthy = operand1_python is not False and operand1_python is not None
             if not op1_truthy: return operand1_python # Mimic Lua return value
             return operand2_python
        elif operator_lua == "or":
             # Lua 'or' returns the first operand if truthy, otherwise the second
             op1_truthy = operand1_python is not False and operand1_python is not None
             if op1_truthy: return operand1_python # Mimic Lua return value
             return operand2_python
        else:
            raise SyntaxError(f"Unsupported operator in simple condition: {operator_lua}")

    # --- Unary Not ---
    elif len(parts) == 2 and parts[0].lower() == "not":
        operand_lua = parts[1]
        operand_python = convertsimplevalues(operand_lua)
        # Lua not: returns true if operand is false or nil, false otherwise
        return operand_python is False or operand_python is None

    # --- Complex conditions need proper parsing (beyond simple split) ---
    # The existing evaluate_condition/convertcondition25 have issues
    # For example, "true and false or true" needs operator precedence.
    elif "and" in parts or "or" in parts or "not" in parts:
         print(f"Warning: Complex condition evaluation ('{val}') is likely incorrect.")
         # return convertcondition25(val) # Keep commented out unless fixed
         return False # Placeholder

    else:
        raise SyntaxError(f"Invalid condition format: {val}")


def evaluate_condition(tokens):
    """Evaluates token list respecting basic 'not', 'and', 'or'. Needs precedence handling."""
    # WARNING: This implementation is basic and doesn't handle operator precedence
    # (e.g., 'and' before 'or') or parentheses correctly.
    
    # Evaluate 'not' first (simple pass)
    processed_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.lower() == "not" and i + 1 < len(tokens):
            operand_val = convertsimplevalues(tokens[i+1])
            # Apply Lua 'not' logic
            processed_tokens.append(operand_val is False or operand_val is None)
            i += 2
        else:
            processed_tokens.append(convertsimplevalues(token))
            i += 1

    if not processed_tokens:
        return True # Or False? Define behavior for empty.

    # Evaluate 'and' and 'or' (left-to-right, incorrect precedence)
    # Lua truthiness: false/nil are false, others true.
    # Lua logical ops: return operand values, not just True/False.
    
    result = processed_tokens[0]
    i = 1
    while i + 1 < len(processed_tokens): # Need operator and next operand
        operator = str(processed_tokens[i]).lower()
        operand = processed_tokens[i+1]
        
        result_truthy = result is not False and result is not None

        if operator == "and":
            if not result_truthy:
                # result already determined (it's falsy), skip operand
                pass # result remains the same
            else:
                result = operand # Move to the second operand
        elif operator == "or":
            if result_truthy:
                 # result already determined (it's truthy), skip operand
                 pass # result remains the same
            else:
                 result = operand # Move to the second operand
        else:
             # If it's not 'and'/'or', maybe it's the start of a new expression?
             # This logic is flawed for complex cases. Assume simple sequence for now.
             # Or raise error?
             print(f"Warning: Unexpected token '{operator}' in condition evaluation.")
             # Attempt to treat 'result' as a standalone truthy value if no more ops
             if i + 2 >= len(processed_tokens):
                 break
             else: # Try to continue, likely wrong
                 result = operand

        i += 2

    # Final result check for truthiness if used in Python context
    # return result is not False and result is not None
    # Return the actual Lua-like value
    return result


def convertcondition25(val):
    """Splits and calls evaluate_condition."""
    # Needs a better tokenizer than split for complex expressions
    tokens = val.split()
    return evaluate_condition(tokens)

# --- Main Interpreter ---

def MNM2(code, local_vars=None):
    """
    Interprets a simple subset of Lua-like code.
    Uses shlex for basic tokenization.
    """
    if local_vars is None:
        local_vars = {} # Initialize if it's the top-level call

    lines = code.strip().split("\n")
    current_line_index = 0

    while current_line_index < len(lines):
        line = lines[current_line_index].strip()
        current_line_index += 1 # Move to next line by default

        if not line or line.startswith('--'): # Skip empty lines and comments
            continue

        # Use shlex for tokenization - handles spaces in quotes
        try:
            tokens = shlex.split(line)
        except ValueError as e:
            print(f"Error tokenizing line: '{line}' - {e}")
            continue # Skip lines with tokenization errors (e.g., unclosed quotes)

        if not tokens:
            continue

        command = tokens[0] # First token is usually the command or variable

        # --- Local Variable/Function Declaration ---
        if command.lower() == "local":
            if len(tokens) < 2:
                print("Syntax Error: 'local' requires a variable name.")
                continue

            # Check for 'local function ...'
            if len(tokens) >= 3 and tokens[1].lower() == "function":
                # --- Function Definition ---
                if len(tokens) < 3:
                    print("Syntax Error: 'local function' requires a function name.")
                    continue

                func_name_raw = tokens[2]
                # Remove trailing () if present
                function_name = func_name_raw[:-2] if func_name_raw.endswith("()") else func_name_raw

                # TODO: Parse arguments list if needed: local function name(arg1, arg2)
                # args = ...

                function_code_lines = []
                nesting_level = 1 # Start at 1 for the initial 'function'

                # Find the corresponding 'end'
                func_start_line_index = current_line_index # Starts after 'local function' line
                func_line_index = func_start_line_index
                found_end = False
                while func_line_index < len(lines):
                    func_line = lines[func_line_index].strip()
                    # Simple check for block keywords - doesn't handle nested blocks perfectly
                    # inside comments or strings.
                    if func_line.lower() in ["function", "if", "for", "while", "do"]: # Add other block starters if needed
                         # Approximation: Assume simple keywords denote nesting
                         if not func_line.lower().startswith("end"): # Avoid double counting 'end function'
                             nesting_level += 1
                    
                    if func_line.lower() == "end":
                        nesting_level -= 1
                        if nesting_level == 0:
                            found_end = True
                            break # Found the matching 'end'
                    elif nesting_level > 0: # Only add lines inside the function body
                         function_code_lines.append(func_line) # Keep original spacing/case

                    func_line_index += 1

                if not found_end:
                    print(f"Syntax Error: Missing 'end' for function definition of '{function_name}'.")
                    # Stop processing further lines in this block as scope is broken
                    current_line_index = len(lines)
                else:
                    function_body_code = "\n".join(function_code_lines)
                    # Create the Python function that will execute the Lua-like code
                    # It captures the *current* local_vars scope (closure)
                    def create_lambda(body, parent_vars):
                         # Need to create a new scope for the function call
                         # Arguments aren't handled yet
                         return lambda: MNM2(body, parent_vars.copy()) # Pass a copy to simulate scope (simple version)

                    defined_function = create_lambda(function_body_code, local_vars)
                    local_vars[function_name] = defined_function
                    print(f"DEBUG: Defined function '{function_name}'")
                    # Skip the lines that formed the function body
                    current_line_index = func_line_index + 1


            # --- Variable Assignment ---
            elif len(tokens) >= 4 and tokens[2] == "=":
                variable_name = tokens[1]
                # Value is the rest of the tokens, joined back (simplistic, assumes simple value)
                # TODO: Handle complex expressions, function calls as values, etc.
                value_token = " ".join(tokens[3:]) # Rejoin might be needed if value has spaces outside quotes
                # Parse the value token (could be literal or another variable)
                local_vars[variable_name] = parse_value(value_token, local_vars)
                # print(f"DEBUG: Assigned local '{variable_name}' = {local_vars[variable_name]}")

            elif len(tokens) == 2: # Declaration without assignment (local x)
                 variable_name = tokens[1]
                 local_vars[variable_name] = None # Initialize to nil/None
                 # print(f"DEBUG: Declared local '{variable_name}' = None")

            else:
                 print(f"Syntax Error: Invalid 'local' statement: {' '.join(tokens)}")


        # --- Print Command ---
        elif command.lower() == "print":
            arguments_to_print = []
            for arg_token in tokens[1:]:
                # Parse each argument token (could be variable or literal)
                parsed_arg = parse_value(arg_token, local_vars)
                # Python's print converts None to "None", True to "True" etc.
                # Mimic Lua's print behavior more closely if needed (e.g., nil prints "nil")
                if parsed_arg is None:
                    arguments_to_print.append("nil")
                elif isinstance(parsed_arg, bool):
                     arguments_to_print.append(str(parsed_arg).lower())
                else:
                     arguments_to_print.append(parsed_arg)
            print(*arguments_to_print) # Use * to unpack args for print

        # --- Function Call ---
        # Check if the first token looks like a function name we know
        # Handle `func()` or `func` (if it's the only token on the line)
        else:
            potential_func_name = command[:-2] if command.endswith("()") else command
            is_call_syntax = command.endswith("()") or len(tokens) == 1 # Allow `func()` or just `func`

            if potential_func_name in local_vars and callable(local_vars[potential_func_name]):
                 if is_call_syntax:
                     # print(f"DEBUG: Calling function '{potential_func_name}'")
                     # TODO: Handle arguments if function call syntax supports them
                     try:
                         # Execute the stored function lambda
                         local_vars[potential_func_name]()
                     except Exception as e:
                         print(f"Error during execution of function '{potential_func_name}': {e}")
                 else:
                     # It's a known function, but not being called directly on its own line
                     # Could be part of an expression later?
                     print(f"Error: Variable '{potential_func_name}' is a function, but wasn't called correctly on this line.")

            # --- Assignment to Existing Variable (Not local) ---
            # VERY basic, assumes `var = value` format
            elif len(tokens) == 3 and tokens[1] == "=":
                 var_name = tokens[0]
                 if var_name in local_vars: # Allow re-assignment
                     value_token = tokens[2]
                     local_vars[var_name] = parse_value(value_token, local_vars)
                     # print(f"DEBUG: Re-assigned '{var_name}' = {local_vars[var_name]}")
                 else:
                     print(f"Error: Cannot assign to unknown variable '{var_name}'. Use 'local' first.")

            # --- End keyword (usually handled during function parsing) ---
            elif command.lower() == "end":
                 # Should generally be consumed by block structures (like function def)
                 # If encountered here, it might be misplaced.
                 print("Warning: Unexpected 'end' keyword encountered.")
                 pass

            # --- Unknown Command ---
            else:
                print(f"Error: Unknown command, variable, or syntax: '{' '.join(tokens)}'")

    return local_vars # Return the final state of variables

# --- Example Usage ---
if __name__ == "__main__":

    print("--- Basic Value Parsing ---")
    # Test convertsimplevalues directly
    print(f"'true' -> {convertsimplevalues('true')}")
    print(f"'nil' -> {convertsimplevalues('nil')}")
    print(f"'123' -> {convertsimplevalues('123')}")
    print("'\"hello world\"' -> " + convertsimplevalues('\"hello world\"')) # String literal
    print(f"'my_var' -> {convertsimplevalues('my_var')}") # Unrecognized -> returns itself

    print("\n--- Running simple PRINT command ---")
    MNM2('print "Hello, MNM!"') # String with space
    MNM2('print 123 false nil "another string"') # Multiple args

    print("\n--- Variable Assignment and Print ---")
    vars1 = MNM2("""
local message = "I am a variable"
local count = 10
print message
print "Count is:", count -- Lua style print with multiple args
local flag = true
print flag nil
""")
    print("Final vars (vars1):", vars1)


    print("\n--- Simple Function Definition and Call ---")
    vars2 = MNM2("""
-- Define a simple function
local function greet()
  local inner_msg = "Inside the function!"
  print inner_msg
  print "Function finished."
end

-- Call the function
print "Calling greet..."
greet()
print "Back from greet."

local another_var = "Global scope"
""")
    print("Final vars (vars2):", vars2)
    # Note: 'greet' in vars2 holds a lambda function object

    print("\n--- Function Call stored function ---")
    # Check if we can call the function from the returned dictionary
    if 'greet' in vars2 and callable(vars2['greet']):
        print("Calling greet again from returned vars...")
        vars2['greet']()
    else:
        print("Could not find callable 'greet' in vars2")

    print("\n--- Test Unknown Command ---")
    MNM2("this is not valid lua")

    print("\n--- Test Function Syntax Error ---")
    MNM2("""
local function broken()
  print "I forgot the end"
-- No end here
local x = 5
""") # Should print missing 'end' error
# Add UI to window...
root = tk.Tk()
root.geometry("800x600")
root.title("UI")
code = tk.Entry(root)
code.pack()
def run():
    rcode = code.get()
    MNM2(str(rcode))
button = tk.Button(root, text="Run", command=run)
button.pack()
root.mainloop()