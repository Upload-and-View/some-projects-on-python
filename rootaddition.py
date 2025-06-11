# muser addition
'''
Put in root folder of muser and rename this file to __init__.py
'''
def DiffNum(num1: None, num2: None):
    if not num1 is None and not num2 is None:
        if isinstance(num1, int) and isinstance(num2, int):
            if num1 == num2:
                return f"{num1} = {num2} Diff_(num1 - num2) = {num1 - num2}"
            elif num1 < num2:
                return f"{num1} < {num2} Diff_(num2 - num1) = {num2 - num1}"
            else:
                return f"{num1} > {num2} Diff_(num1 - num2) = {num1 - num2}"
        else:
            if isinstance(num1, bool):
                raise TypeError("DiffNum() takes numbers, but in num1 bool were given")
            elif isinstance(num2, bool):
                raise TypeError("DiffNum() takes numbers, but in num2 bool were given")
            elif isinstance(num2, str):
                raise TypeError("DiffNum() takes numbers, but in num2 string were given")
            elif isinstance(num1, str):
                raise TypeError("DiffNum() takes numbers, but in num1 string were given")
            else:
                raise TypeError("DiffNum() takes numbers, but unknown type were given")

    else:
        raise TypeError("DiffNum() takes numbers, but None type were given")

def custommath(operation: None, func: None):
    operations_list: list = []
    numbers_list: list = []
    if not operation is None and not func is None:
        if isinstance(operation, str):
            tokens = operation.split(" ")
            for token in tokens:
                if token == "+":
                    operations_list.append("add")
                elif token == "-":
                    operations_list.append("sub")
                elif token == "^":
                    operations_list.append("pow")
                elif token == "*":
                    operations_list.append("mul")
                elif token == "/":
                    operations_list.append("div")
                elif token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
                    numbers_list.append(int(token))
                elif '.' in token and all(part.isdigit() for part in token.split('.')):
                    try:
                        numbers_list.append(float(token))
                    except ValueError:
                        pass # Ignore if conversion fails
                elif token.startswith('-') and '.' in token[1:] and all(part.isdigit() for part in token[1:].split('.')):
                    try:
                        numbers_list.append(float(token))
                    except ValueError:
                        pass # Ignore if conversion fails

            if func is not None and callable(func):
                result = None
                num1 = numbers_list[0] if len(numbers_list) > 0 else None
                num2 = numbers_list[1] if len(numbers_list) > 1 else None

                if operations_list:
                    op = operations_list[0] # Assuming only one operation for now

                    if op == "add" and num1 is not None and num2 is not None:
                        result = func(num1 + num2)
                    elif op == "sub" and num1 is not None and num2 is not None:
                        result = func(num1 - num2)
                    elif op == "mul" and num1 is not None and num2 is not None:
                        result = func(num1 * num2)
                    elif op == "div" and num1 is not None and num2 is not None:
                        if num2 != 0:
                            result = func(num1 / num2)
                        else:
                            return "Error: Division by zero"
                    elif op == "pow" and num1 is not None and num2 is not None:
                        result = func(num1 ** num2)
                    elif num1 is not None:
                        result = func(num1) # If no operation, just apply function to the first number

                return result
        else:
            raise TypeError("custommath() takes a string for operation")
    else:
        raise TypeError("custommath() requires both operation and func arguments")

if __name__ == "__main__":
    print(DiffNum(6, 7))

    def square(n):
        return n * n

    print(custommath("5 + 3", square))
    print(custommath("10 - 2", square))
    print(custommath("4 * 6", square))
    print(custommath("9 / 3", square))
    print(custommath("2 ^ 5", square))
    print(custommath("-7", abs))
    print(custommath("3.14159", round))
    print(custommath("-2.71828 + 1.0", int))