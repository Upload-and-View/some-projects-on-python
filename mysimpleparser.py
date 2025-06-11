import re
import shlex #SHLEX AAAAAAAAAAAAA

content = "Test"

def post(val):
    global content
    if val is not None:
        if isinstance(val, list) and len(val) == 1:
            content = val[0]
        elif not isinstance(val, list):
            content = val
        else:
            print("Recommended to use POST on a single value")
            content = val
    else:
        return "ERROR"
    return content

def delete():
    global content
    content = None
    return "OK"

def get():
    return content

def head():
    value = get()
    if value is None:
        return "ERROR"
    elif value == content:
        return "OK"
    elif value: # Check if it's not an empty string
        return "OK"
    return "ERROR"

def put(val):
    global content
    try:
        content = f"FILE: {str(val)}"
        return "OK"
    except Exception:
        return "ERROR"

def connect():
    if content is None:
        return "ERROR"
    else:
        return "OK"

def patch(val):
    global content
    if val is None:
        return "ERROR"
    if isinstance(val, list):
        content += " ".join(val)
    else:
        content += str(val)
    return content

def options():
    table = {
        "Value": get(),
        "Version": "1.0 / SimulateRequests"
    }
    return table

def parser(code):
    if code is None or not isinstance(code, str):
        raise Exception("Tried to use parser on a non-string, or non-existent string")

    lines = re.split(r"\n", code)
    results = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            partofcode = shlex.split(line)
            if not partofcode:
                continue
            command = partofcode[0].lower()
            args = partofcode[1:]
            result = None

            if command == "post":
                result = post(args[0] if args else None)
            elif command == "delete":
                result = delete()
            elif command == "get":
                result = get()
            elif command == "head":
                result = head()
            elif command == "put":
                result = put(args[0] if args else None)
            elif command == "connect":
                result = connect()
            elif command == "patch":
                result = patch(args[0] if args else None)
            elif command == "options":
                result = options()
            else:
                raise Exception(f"No command found: {command}")

            if result is not None:
                results.append(result)

        except ValueError as e:
            print(f"Error parsing line '{line}': {e}")
        except Exception as e:
            print(f"Error executing command on line '{line}': {e}")

    if not results:
        print("No results.")
    else:
        for num, res in enumerate(results, start=1):  # Start numbering from 1
            if isinstance(res, dict):
                for key, value in res.items():
                    print(f"Result {num}: {key} - {value}")
            else:
                print(f"Result {num}: {res}")

if __name__ == "__main__":
    codee = '''
    get
    patch Hello
    post World
    get
    options
    put "My File Content"
    get
    '''
    parser(codee)