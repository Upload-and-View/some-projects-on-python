# PLua (Lua to Python) - MNM (Muser Not Matters) v3.1 (Control Flow)
# Updated by Muser (New Big Update (NBU))
# Enhanced by AI (Control Flow Implementation)

import re
import shlex
from typing import Any, Dict, List, Tuple, Optional
import tkinter as tk
import sys
from io import StringIO

# --- Utility Functions ---

def lua_gsub(text, pattern, replacement):
    """Mimics Lua's string.gsub function."""
    # ... (previous code remains unchanged) ...
    count = 0
    if callable(replacement):
        def replace_func(match):
            nonlocal count
            count += 1
            return replacement(*match.groups())
        modified_text = re.sub(pattern, replace_func, text)
    else:
        modified_text, count = re.subn(pattern, replacement, text)
    return modified_text, count


def convertsimplevalues(val: str) -> Any:
    """Converts string representation of simple Lua values to Python types."""
    # ... (previous code remains unchanged) ...
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
            if val.replace('.', '', 1).replace('-', '', 1).isdigit(): return float(val)
            else: return val
        except ValueError: return val


def parse_value(token: str, local_vars: dict) -> Any:
    """Parses a token into a Python value, checking variables first."""
    # ... (previous code remains unchanged) ...
    if token in local_vars: return local_vars[token]
    return convertsimplevalues(token)

# --- Condition Evaluation ---

def evaluate_lua_condition(condition_tokens: List[str], local_vars: Dict[str, Any]) -> bool:
    """
    Evaluates a list of condition tokens based on Lua truthiness.
    Handles simple cases: single values, not, binary comparisons.
    WARNING: Does NOT correctly handle operator precedence for complex 'and'/'or' chains.
    """
    if not condition_tokens:
        print("Warning: Empty condition evaluated as false.")
        return False # Empty condition is likely false?

    # --- Unary Not ---
    if len(condition_tokens) >= 2 and condition_tokens[0].lower() == "not":
        operand_val = parse_value(condition_tokens[1], local_vars)
        # Handle potential further complexity? No, keep it simple for now.
        if len(condition_tokens) > 2:
             print(f"Warning: Condition complexity after 'not' ignored: {' '.join(condition_tokens[2:])}")
        # Lua not: returns true only if operand is false or nil
        return operand_val is False or operand_val is None

    # --- Single Value Truthiness ---
    elif len(condition_tokens) == 1:
        py_val = parse_value(condition_tokens[0], local_vars)
        # Lua truthiness: false and nil are false, everything else is true
        return py_val is not False and py_val is not None

    # --- Binary Operation ---
    elif len(condition_tokens) == 3:
        op1_token = condition_tokens[0]
        operator = condition_tokens[1]
        op2_token = condition_tokens[2]

        operand1 = parse_value(op1_token, local_vars)
        operand2 = parse_value(op2_token, local_vars)

        try:
            if operator == "==": return operand1 == operand2
            elif operator == "~=": return operand1 != operand2
            elif operator == "<": return operand1 < operand2
            elif operator == ">": return operand1 > operand2
            elif operator == "<=": return operand1 <= operand2
            elif operator == ">=": return operand1 >= operand2
            # Basic 'and'/'or' - WARNING: Incorrect precedence for chains!
            elif operator.lower() == "and":
                 # Evaluate truthiness of first operand
                 op1_truthy = operand1 is not False and operand1 is not None
                 # Return Python boolean equivalent of Lua logic
                 return op1_truthy and (operand2 is not False and operand2 is not None)
            elif operator.lower() == "or":
                 op1_truthy = operand1 is not False and operand1 is not None
                 return op1_truthy or (operand2 is not False and operand2 is not None)
            else:
                print(f"Error: Unsupported operator in condition: {operator}")
                return False
        except TypeError:
            # Handle cases like comparing number and string/nil
            print(f"Warning: Type error during condition evaluation ('{operand1}' {operator} '{operand2}'). Resulting in false.")
            if operator == "~=": # Not equal is often true for different types (except nil comparison)
                 return True # Simplification
            return False
        except Exception as e:
             print(f"Error during condition evaluation: {e}")
             return False

    # --- Complex conditions (and/or chains) - Not properly supported ---
    else:
        print(f"Warning: Complex condition evaluation is not fully supported: '{' '.join(condition_tokens)}'. Evaluating as false.")
        # Attempt basic left-to-right? No, too error prone without parser.
        return False


# --- Block Structure Parsing ---
BlockInfo = Dict[str, Any] # Type hint for return value

def find_block_structure(lines: List[str], start_index: int) -> Optional[BlockInfo]:
    """
    Finds the structure of an if/while block starting at start_index.
    Returns a dictionary containing line indices for 'if'/'while', 'elseif', 'else', 'end',
    and the extracted lines for each block. Returns None if structure is invalid.

    Example return for if-elseif-else-end:
    {
        'type': 'if',
        'if_cond_tokens': ['a', '>', 'b'],
        'if_block_lines': ['print a'],
        'if_block_start_line': start_index + 1,
        'elseifs': [
            { 'cond_tokens': ['a', '<', '0'], 'block_lines': ['print "neg"'], 'block_start_line': N }
        ],
        'else_block_lines': ['print "other"'],
        'else_block_start_line': M,
        'end_line': end_index
    }
    Example return for while-do-end:
     {
        'type': 'while',
        'while_cond_tokens': ['i', '<', '10'],
        'while_block_lines': ['print i', 'i = i + 1'],
        'while_block_start_line': start_index + 1,
        'end_line': end_index
    }
    """
    if start_index >= len(lines):
        return None

    line = lines[start_index].strip()
    try:
        tokens = shlex.split(line)
    except ValueError:
        print(f"Error tokenizing block start line: {line}")
        return None

    if not tokens: return None
    block_type = tokens[0].lower()

    structure: BlockInfo = {'type': block_type, 'elseifs': [], 'end_line': -1}
    nesting_level = 1
    current_line_index = start_index + 1
    last_block_start = current_line_index

    # --- Parse Initial Condition (if/while) ---
    if block_type == "if":
        if "then" not in tokens:
            print(f"Syntax Error: Missing 'then' in 'if' statement on line {start_index + 1}")
            return None
        then_index = tokens.index("then")
        structure['if_cond_tokens'] = tokens[1:then_index]
        structure['if_block_start_line'] = current_line_index
    elif block_type == "while":
        if "do" not in tokens:
            print(f"Syntax Error: Missing 'do' in 'while' statement on line {start_index + 1}")
            return None
        do_index = tokens.index("do")
        structure['while_cond_tokens'] = tokens[1:do_index]
        structure['while_block_start_line'] = current_line_index
    else:
        return None # Should not happen if called correctly

    current_block_lines = []

    # --- Scan for structure elements ---
    while current_line_index < len(lines):
        scan_line = lines[current_line_index].strip()
        try:
            scan_tokens = shlex.split(scan_line)
        except ValueError:
            scan_tokens = [] # Treat tokenization error line as non-keyword line

        keyword = scan_tokens[0].lower() if scan_tokens else ""

        # Handle nesting - Simple keyword check (limitation: fails on keywords in strings/comments)
        block_starters = ["if", "while", "function", "for", "do"] # 'do' for plain blocks if supported later
        if keyword in block_starters and keyword != "end": # Don't double count 'end function' etc.
             nesting_level += 1

        if keyword == "end":
            nesting_level -= 1
            if nesting_level == 0: # Found the matching end for our block
                structure['end_line'] = current_line_index
                # Store lines of the last block segment (if/elseif/else/while)
                if block_type == 'if':
                    if 'else_block_start_line' in structure:
                        structure['else_block_lines'] = lines[structure['else_block_start_line']:current_line_index]
                    elif structure['elseifs']:
                         structure['elseifs'][-1]['block_lines'] = lines[structure['elseifs'][-1]['block_start_line']:current_line_index]
                    else:
                         structure['if_block_lines'] = lines[structure['if_block_start_line']:current_line_index]
                elif block_type == 'while':
                    structure['while_block_lines'] = lines[structure['while_block_start_line']:current_line_index]

                #print(f"DEBUG: Found block structure ending at {current_line_index}: {structure}")
                return structure
            elif nesting_level < 0:
                 print(f"Syntax Error: Unexpected 'end' on line {current_line_index + 1}")
                 return None # Mismatched end
            else: # End of a nested block
                 current_block_lines.append(scan_line) # Add line to current block

        elif nesting_level == 1 and block_type == "if": # Only look for elseif/else at the top level of this if
            if keyword == "elseif":
                if "then" not in scan_tokens:
                    print(f"Syntax Error: Missing 'then' in 'elseif' on line {current_line_index + 1}")
                    return None
                then_index = scan_tokens.index("then")
                cond_tokens = scan_tokens[1:then_index]

                # Store lines of the previous block (if or previous elseif)
                if structure['elseifs']: # Previous was elseif
                     structure['elseifs'][-1]['block_lines'] = lines[structure['elseifs'][-1]['block_start_line']:current_line_index]
                else: # Previous was if
                     structure['if_block_lines'] = lines[structure['if_block_start_line']:current_line_index]

                structure['elseifs'].append({
                    'cond_tokens': cond_tokens,
                    'block_start_line': current_line_index + 1
                })
                last_block_start = current_line_index + 1

            elif keyword == "else":
                # Store lines of the previous block (if or last elseif)
                if structure['elseifs']: # Previous was elseif
                     structure['elseifs'][-1]['block_lines'] = lines[structure['elseifs'][-1]['block_start_line']:current_line_index]
                else: # Previous was if
                     structure['if_block_lines'] = lines[structure['if_block_start_line']:current_line_index]

                structure['else_block_start_line'] = current_line_index + 1
                last_block_start = current_line_index + 1
            else: # Regular line within the current block
                 pass # Line will be added when the block terminates

        #else: # Line within a block (nested or top level)
            # Don't add lines here, wait until block end is found to grab slices

        current_line_index += 1

    # If loop finishes without finding end
    print(f"Syntax Error: Missing 'end' for block starting on line {start_index + 1}")
    return None


# --- Main Interpreter ---

def MNM2(code, local_vars=None, is_block_execution=False): # Added flag
    """
    Interprets a simple subset of Lua-like code.
    Uses shlex for basic tokenization.
    Handles local vars/funcs, print, if/elseif/else, while.
    """
    if local_vars is None:
        local_vars = {}

    # Avoid splitting if already executing a block (lines passed directly)
    lines = code if is_block_execution else code.strip().split("\n")
    current_line_index = 0
    exit_code = 0 # For potential future use (e.g., break, return)

    while current_line_index < len(lines):
        line_number = current_line_index # Keep track for error messages if needed
        line = lines[current_line_index].strip()

        # Default behavior: advance to next line unless control flow jumps
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

        command = tokens[0].lower()

        # --- Local Variable/Function Declaration ---
        if command == "local":
            # ... (previous local handling code - unchanged) ...
            if len(tokens) < 2: print("Syntax Error: 'local' requires a variable name."); current_line_index=next_line_index; continue
            if len(tokens) >= 3 and tokens[1].lower() == "function":
                if len(tokens) < 3: print("Syntax Error: 'local function' requires a function name."); current_line_index=next_line_index; continue
                func_name_raw = tokens[2]
                function_name = func_name_raw[:-2] if func_name_raw.endswith("()") else func_name_raw
                func_structure = find_block_structure(lines, current_line_index) # Use find_block_structure logic loosely here for end finding
                if func_structure and func_structure['end_line'] != -1:
                     # Simplified: grab all lines between def and end
                     function_code_lines = lines[current_line_index + 1 : func_structure['end_line']]
                     function_body_code = "\n".join(function_code_lines)
                     def create_lambda(body, parent_vars): return lambda: MNM2(body.split("\n"), parent_vars.copy(), is_block_execution=True) # Pass lines list
                     defined_function = create_lambda(function_body_code, local_vars)
                     local_vars[function_name] = defined_function
                     #print(f"DEBUG: Defined function '{function_name}'")
                     next_line_index = func_structure['end_line'] + 1 # Jump past function end
                else:
                     print(f"Syntax Error: Missing 'end' for function '{function_name}'.")
                     next_line_index = len(lines) # Stop processing
            elif len(tokens) >= 4 and tokens[2] == "=":
                variable_name = tokens[1]
                value_token = " ".join(tokens[3:])
                local_vars[variable_name] = parse_value(value_token, local_vars)
            elif len(tokens) == 2:
                 local_vars[tokens[1]] = None
            else: print(f"Syntax Error: Invalid 'local' statement: {' '.join(tokens)}")
            # --- End of local handling ---

        # --- Print Command ---
        elif command == "print":
            # ... (previous print handling code - unchanged) ...
            arguments_to_print = []
            for arg_token in tokens[1:]:
                parsed_arg = parse_value(arg_token, local_vars)
                if parsed_arg is None: arguments_to_print.append("nil")
                elif isinstance(parsed_arg, bool): arguments_to_print.append(str(parsed_arg).lower())
                else: arguments_to_print.append(parsed_arg)
            print(*arguments_to_print)
            # --- End of print handling ---

        # --- If Statement ---
        elif command == "if":
            structure = find_block_structure(lines, current_line_index)
            if not structure or structure['type'] != 'if':
                print(f"Syntax Error: Invalid 'if' structure starting line {line_number + 1}")
                next_line_index = len(lines) # Stop processing
            else:
                executed_block = False
                # Evaluate main 'if' condition
                if evaluate_lua_condition(structure['if_cond_tokens'], local_vars):
                    #print(f"DEBUG: Executing IF block lines {structure['if_block_start_line']} to {structure['elseifs'][0]['block_start_line'] if structure['elseifs'] else (structure.get('else_block_start_line', structure['end_line']))}")
                    MNM2(structure['if_block_lines'], local_vars, is_block_execution=True)
                    executed_block = True
                else:
                    # Evaluate 'elseif' conditions
                    for elseif_block in structure['elseifs']:
                        if evaluate_lua_condition(elseif_block['cond_tokens'], local_vars):
                           #print(f"DEBUG: Executing ELSEIF block lines {elseif_block['block_start_line']} ...")
                           MNM2(elseif_block['block_lines'], local_vars, is_block_execution=True)
                           executed_block = True
                           break # Only execute the first matching elseif
                # Evaluate 'else' block if no other block executed
                if not executed_block and 'else_block_start_line' in structure:
                    #print(f"DEBUG: Executing ELSE block lines {structure['else_block_start_line']} ...")
                    MNM2(structure['else_block_lines'], local_vars, is_block_execution=True)

                # Jump program counter past the entire if/elseif/else/end structure
                next_line_index = structure['end_line'] + 1

        # --- While Statement ---
        elif command == "while":
             structure = find_block_structure(lines, current_line_index)
             if not structure or structure['type'] != 'while':
                 print(f"Syntax Error: Invalid 'while' structure starting line {line_number + 1}")
                 next_line_index = len(lines) # Stop processing
             else:
                 loop_count = 0
                 max_loops = 1000 # Safety break for infinite loops

                 while loop_count < max_loops:
                     # Evaluate condition BEFORE executing block
                     if evaluate_lua_condition(structure['while_cond_tokens'], local_vars):
                         #print(f"DEBUG: Executing WHILE block (iteration {loop_count+1})...")
                         MNM2(structure['while_block_lines'], local_vars, is_block_execution=True)
                         loop_count += 1
                     else:
                         #print(f"DEBUG: WHILE condition false, exiting loop.")
                         break # Condition is false, exit loop
                 else:
                      # Safety break triggered
                      print(f"Error: Maximum loop iterations ({max_loops}) reached for 'while' starting line {line_number + 1}. Assuming infinite loop.")

                 # Jump program counter past the end of the while block
                 next_line_index = structure['end_line'] + 1


        # --- Function Call ---
        elif tokens[0] in local_vars and callable(local_vars[tokens[0]]): # Simplified check
             potential_func_name = tokens[0]
             # Basic call: func() or func name on its own line
             is_call_syntax = line.endswith("()") or len(tokens) == 1
             if is_call_syntax:
                 try:
                     local_vars[potential_func_name]()
                 except Exception as e:
                     print(f"Error during execution of function '{potential_func_name}': {e}")
             else:
                  print(f"Error: Variable '{potential_func_name}' is a function, but wasn't called correctly on this line.")

        # --- Assignment to Existing Variable ---
        elif len(tokens) == 3 and tokens[1] == "=" and tokens[0] in local_vars:
             var_name = tokens[0]
             value_token = tokens[2]
             local_vars[var_name] = parse_value(value_token, local_vars)

        # --- End keyword (usually handled by block parsing) ---
        elif command == "end" or command == "then" or command == "do" or command == "else" or command == "elseif":
             # These keywords should only appear as part of a structure
             # If encountered directly, it's likely a syntax error or part of skipped block
             # find_block_structure should handle valid cases. We might land here if skipping.
             # print(f"Warning: Unexpected '{command}' keyword encountered directly on line {line_number + 1}.")
             pass # Just go to the next line

        # --- Unknown Command / Potential Assignment to Undeclared Var ---
        else:
             # Check for potential assignment to undeclared global (error in strict MNM)
             if len(tokens) == 3 and tokens[1] == "=":
                  print(f"Error: Cannot assign to unknown variable '{tokens[0]}' on line {line_number + 1}. Use 'local' first.")
             else:
                  print(f"Error: Unknown command, variable, or syntax on line {line_number + 1}: '{' '.join(tokens)}'")

        # --- Move to the next line ---
        current_line_index = next_line_index

    return local_vars

# --- Example Usage ---
if __name__ == "__main__":

    # ... (previous examples remain unchanged) ...

    print("\n--- If/Elseif/Else Test ---")
    MNM2("""
local x = 10
local y = 5
local z = 10
local name = "MNM"

print "--- If tests ---"
if x > y then
  print "x is greater than y (correct)"
end

if x < y then
  print "x is less than y (should not print)"
else
  print "x is not less than y (else block)"
end

if name == "Lua" then
  print "Name is Lua"
elseif name == "MNM" then
  print "Name is MNM (elseif block)"
else
  print "Name is something else"
end

if x ~= z then
  print "x is not equal to z (should not print)"
elseif y > 0 and y < 10 then
  print "y is between 0 and 10 (complex elseif - precedence may be simple)"
end

if false then
  print "This is false"
elseif nil then
  print "This is nil"
else
  print "Reached final else"
end
""")

    print("\n--- While Loop Test ---")
    MNM2("""
local counter = 0
print "--- While loop ---"
while counter < 5 do
  print "Counter:", counter
  counter = counter + 1 -- Need to implement arithmetic operations properly for this
                        -- Simple assignment works, but calculation needs a parser
                        -- Workaround: Assign literal value
  if counter == 1 then local temp = 0 end -- Test assignment inside loop
  if counter == 2 then counter = 3 end -- Jump value
  if counter == 3 then counter = 4 end
  if counter == 4 then counter = 5 end

end
print "Loop finished. Final counter:", counter

local countdown = 2
while countdown > 0 do
  print "Countdown:", countdown
  if countdown == 2 then countdown = 1 end -- Manual decrement
  if countdown == 1 then countdown = 0 end
end
print "Countdown finished"

local condition = true
local safety = 0
while condition and safety < 3 do -- Test 'and' in condition (simple eval)
   print "Condition loop, safety:", safety
   safety = safety + 1
   if safety == 1 then condition = true end # Simulate calculation
   if safety == 2 then condition = true end
   if safety == 3 then condition = false end # Make condition false
end
print "Condition loop finished"

""")

# --- UI Section ---
def run():
    rcode = code_input_area.get("1.0", tk.END)
    MNM2(rcode) # Assume MNM2 handles its own output now via print

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


def run_mnm_code():
    mnm_code = code_input_area.get("1.0", tk.END)
    redirected_output = StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr # Redirect errors too
    sys.stdout = redirected_output
    sys.stderr = redirected_output # Send print statements from errors here too
    try:
        MNM2(mnm_code) # Pass the code string directly
    except Exception as e:
        # Catch errors from the interpreter itself if they escape MNM2's handling
        print(f"\n--- Interpreter Error ---") # Use print to go to redirected output
        print(f"Error during execution:\n{e}")
        import traceback
        print(traceback.format_exc())
        print(f"-------------------------\n")
    finally:
        sys.stdout = original_stdout # Restore stdout
        sys.stderr = original_stderr # Restore stderr
        output = redirected_output.getvalue()
        output_area.config(state=tk.NORMAL)
        output_area.delete("1.0", tk.END)
        #output_area.insert(tk.END, "--- MNM Output ---\n")
        output_area.insert(tk.END, output)
        #output_area.insert(tk.END, "------------------\n")
        output_area.config(state=tk.DISABLED)

# --- Tkinter Setup ---
root = tk.Tk()
root.title("MNM V3.1 Interpreter (Control Flow)")

# Input area
input_frame = tk.Frame(root)
input_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
code_label = tk.Label(input_frame, text="Enter MNM Code:")
code_label.pack(anchor=tk.W)
code_input_area = tk.Text(input_frame, height=20, width=80, undo=True)
code_input_area.pack(fill=tk.BOTH, expand=True)
code_input_area.bind("<KeyRelease>", highlight_syntax) # Highlight on key release

# Button
run_button = tk.Button(root, text="Run MNM Code", command=run_mnm_code)
run_button.pack(pady=5)

# Output area
output_frame = tk.Frame(root)
output_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
output_label = tk.Label(output_frame, text="Output:")
output_label.pack(anchor=tk.W)
output_area = tk.Text(output_frame, height=10, width=80, state=tk.DISABLED, wrap=tk.WORD)
output_area.pack(fill=tk.BOTH, expand=True)

# Initial highlight
highlight_syntax()

root.mainloop()