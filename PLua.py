# PLua (Lua to Python)
import warnings
warnings.warn("this code is deprecated, use MNM, or MNM V2", DeprecationWarning)

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
            return val
if __name__ == "__main__":
    print("Hello!")
    print(f"Convertcondition2: 1: {str(convertcondition25('true and not false'))}")
    

    # Example usage
    print("Convertcondition: 1: " + str(convertcondition("true")))
    print("Convertcondition: 2: " + str(convertcondition("false")))
    print("Convertcondition: 3: " + str(convertcondition("5 == 5")))
    print("Convertcondition: 4: " + str(convertcondition("10 > 20")))
    print("Convertcondition: 5: " + str(convertcondition("not true")))
    print("Convertsimplevalues: 1: " + str(convertsimplevalues("nil")))
    print("Convertsimplevalues: 2: " + str(convertsimplevalues("true")))
    print("Convertsimplevalues: 3: " + str(convertsimplevalues("123")))
    print("Convertsimplevalues: 4: " + str(convertsimplevalues("3.14")))
    print("Convertsimplevalues: 5: " + str(convertsimplevalues("hello")))