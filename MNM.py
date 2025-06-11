# PLua (Lua to Python)
# Now is MNM (Muser Not Matters)
import re

def lua_gsub(text, pattern, replacement):
    """
    Mimics Lua's string.gsub function.
    """
    count = 0
    if callable(replacement):
        def replace_func(match):
            nonlocal count
            count += 1
            return replacement(match)
        modified_text = re.sub(pattern, replace_func, text)
    else:
        modified_text, count = re.subn(pattern, replacement, text)
    return modified_text, count

def convertsimplevalues(val):
    if val == "nil":
        return None
    elif val == "false":
        return False
    elif val == "true":
        return True
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val  # If it's not a simple type, return it as is for now

def convertcondition(val):
    parts = val.split()
    if not parts:
        return True  # Empty condition is often true

    if len(parts) == 1:
        return convertsimplevalues(parts[0]) # Treat single value as condition

    if len(parts) == 3:
        operand1_lua = parts[0]
        operator_lua = parts[1]
        operand2_lua = parts[2]

        operand1_python = convertsimplevalues(operand1_lua)
        operand2_python = convertsimplevalues(operand2_lua)

        if operator_lua == "==":
            return operand1_python == operand2_python
        elif operator_lua == "~=":
            return operand1_python != operand2_python
        elif operator_lua == "<":
            return operand1_python < operand2_python
        elif operator_lua == ">":
            return operand1_python > operand2_python
        elif operator_lua == "<=":
            return operand1_python <= operand2_python
        elif operator_lua == ">=":
            return operand1_python >= operand2_python
        elif operator_lua == "and":
            return operand1_python and operand2_python
        elif operator_lua == "or":
            return operand1_python or operand2_python
        else:
            raise SyntaxError(f"Unsupported operator: {operator_lua}")
    elif len(parts) == 2 and parts[0] == "not":
        operand_lua = parts[1]
        operand_python = convertsimplevalues(operand_lua)
        return not operand_python
    elif "and" in parts:
        convertcondition25(val)
    elif "or" in parts:
        convertcondition25(val)
    else:
        raise SyntaxError(f"Invalid condition format: {val}")

def evaluate_condition(tokens):
    # Evaluate 'not' first
    new_tokens = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "not" and i + 1 < len(tokens):
            new_tokens.append(not convertsimplevalues(tokens[i+1]))
            i += 2
        else:
            new_tokens.append(convertsimplevalues(tokens[i]))
            i += 1

    # Now evaluate 'and' and 'or' on the new_tokens (which might contain booleans)
    result = new_tokens[0]
    i = 1
    while i < len(new_tokens):
        operator = new_tokens[i]
        operand = new_tokens[i+1]
        if operator == "and":
            result = result and operand
        elif operator == "or":
            result = result or operand
        i += 2
    return result

def convertcondition25(val):
    tokens = val.split()
    return evaluate_condition(tokens)

def MNM2(code):
    # Parser
    tokens: list = []
    tokenval = 0
    lines: list = code.split("\n")
    for v in lines:
        token = v.split(" ")
        tokens.append(token)  # Append the list of tokens from the line
        tokenval += 1

    for i in tokens:
        if i[0].lower() == "print":  # Access the first element of the inner list
            arguments_to_print = []
            for arg_token in i[1:]:
                if arg_token.lower() == "true":
                    arguments_to_print.append(True)
                elif arg_token.lower() == "false":
                    arguments_to_print.append(False)
                elif arg_token.lower() == "nil":
                    arguments_to_print.append(None)
                elif arg_token.isdigit() or (arg_token.startswith('-') and arg_token[1:].isdigit()):
                    arguments_to_print.append(int(arg_token))
                elif '.' in arg_token and all(part.isdigit() for part in arg_token.split('.')):
                    try:
                        arguments_to_print.append(float(arg_token))
                    except ValueError:
                        arguments_to_print.append(arg_token.strip('"')) # Treat as string if float conversion fails
                elif arg_token.startswith('-') and '.' in arg_token[1:] and all(part.isdigit() for part in arg_token[1:].split('.')):
                    try:
                        arguments_to_print.append(float(arg_token))
                    except ValueError:
                        arguments_to_print.append(arg_token.strip('"')) # Treat as string if float conversion fails
                else:
                    arguments_to_print.append(arg_token.strip('"'))  # Treat as string by default

            print(*arguments_to_print)

def MuserNotMatters(code):
    lowercode = code.lower()
    simple_value = convertsimplevalues(lowercode)
    if simple_value != code:  # If it was a simple value ("true", "false", "nil")
        return simple_value
    else:
        MNM2(code) # If not a simple value, try to parse it with MNM2

if __name__ == "__main__":
    print("MuserNotMatters(\"true\"): " + str(MuserNotMatters("true")))
    print("MuserNotMatters(\"false\"): " + str(MuserNotMatters("false")))
    print("MuserNotMatters(\"nil\"): " + str(MuserNotMatters("nil")))
    print("MuserNotMatters(\"123\"): " + str(MuserNotMatters("123")))
    print("MuserNotMatters(\"3.14\"): " + str(MuserNotMatters("3.14")))
    print("MuserNotMatters(\"hello\"): " + str(MuserNotMatters("hello")))

    print("MNM2(\"PRINT \\\"HI\\\"\") output:")
    MNM2("PRINT \"HI\"")

    print("MNM2(\"PRINT \\\"\\xe7\\\"\") output:")
    MNM2("PRINT \"\\xe7\"")
    MNM2("print \"This should be a non-direct cedilla: \xe7\"")
    MNM2("print \"This should be a directcedilla: ç\"") # Added a direct print for verification
    print("\nPLua Examples:")
    print("Convertcondition: 1: " + str(convertcondition("true")))
