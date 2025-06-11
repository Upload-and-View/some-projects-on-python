import re
import shlex
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

variables: dict = {}

def colored_output(text, color=Fore.WHITE):
    print(color + text + Style.RESET_ALL)

def system_output(arguments):
    output = []
    for arg in arguments:
        if arg in variables:
            output.append(variables[arg])
        else:
            output.append(arg)
    colored_output(" ".join(output), Fore.GREEN)
    return None

def system_input(arguments):
    prompt = colored_output(" ".join(arguments) + " ", Fore.YELLOW) if arguments else colored_output("", Fore.YELLOW)
    return input(prompt)

def interpreter(tokens):
    if not tokens:
        return None

    command = tokens[0].lower()

    if command.startswith("system."):
        parts = command.split('.', 1)
        if len(parts) == 2:
            sub_command = parts[1]
            if sub_command == "output":
                return system_output(tokens[1:])
            elif sub_command == "input":
                return system_input(tokens[1:])
            else:
                colored_output(f"Unknown system command: {sub_command}", Fore.RED)
                return None
        else:
            colored_output(f"Invalid system command format: {command}", Fore.RED)
            return None
    elif command == "let":
        if len(tokens) == 5 and tokens[1] == "=" and tokens[2].lower() == "system.input" and (tokens[4].startswith('"') and tokens[4].endswith('"') or tokens[4].startswith("'") and tokens[4].endswith("'")):
            variable_name = tokens[0]
            prompt = tokens[4][1:-1]
            user_input = system_input([prompt])
            variables[variable_name] = user_input
            return None
        elif len(tokens) == 5 and tokens[1] == "=" and tokens[2].lower() == "system.input":
            # Handle the case where the prompt is the rest of the tokens after system.input
            prompt_parts = tokens[3:]
            prompt = " ".join(prompt_parts).strip()
            if prompt.startswith('"') and prompt.endswith('"'):
                variable_name = tokens[0]
                user_input = system_input([prompt[1:-1]])
                variables[variable_name] = user_input
                return None
            elif prompt.startswith("'") and prompt.endswith("'"):
                variable_name = tokens[0]
                user_input = system_input([prompt[1:-1]])
                variables[variable_name] = user_input
                return None
            else:
                variable_name = tokens[0]
                user_input = system_input([prompt]) # Try without assuming quotes
                variables[variable_name] = user_input
                return None
        elif len(tokens) >= 3 and tokens[1] == "=":
            variable_name = tokens[0]
            variable_value_parts = tokens[2:]
            variable_value = " ".join(variable_value_parts).strip()
            if variable_value.startswith('"') and variable_value.endswith('"'):
                variables[variable_name] = variable_value[1:-1]
            elif variable_value.startswith("'") and variable_value.endswith("'"):
                variables[variable_name] = variable_value[1:-1]
            else:
                variables[variable_name] = variable_value
            return None
        else:
            colored_output("Syntax error: Invalid variable assignment. Usage: let <variable> = <value> or let <variable> = system.input(\"prompt\")", Fore.RED)
            return None
    elif command == "print":
        output = []
        for arg in tokens[1:]:
            if arg in variables:
                output.append(variables[arg])
            elif arg.startswith('"') and arg.endswith('"'):
                output.append(arg[1:-1])
            elif arg.startswith("'") and arg.endswith("'"):
                output.append(arg[1:-1])
            else:
                output.append(arg)
        colored_output(" ".join(output), Fore.BLUE)
        return None
    else:
        colored_output(f"Unknown command: {command}", Fore.RED)
        return None

def parser(code):
    lines = re.split(r"\n", code)
    for line in lines:
        if not line.strip():
            continue
        if line.strip().startswith("#"):
            continue

        tokens = shlex.split(line)
        print(f"{Fore.YELLOW}Tokens for line '{line.strip()}': {tokens}{Style.RESET_ALL}") # Debugging: Print the tokens
        interpreter(tokens)

if __name__ == "__main__":
    codee = """
system.output "Hello with colorama!"
let username = system.input(\"Enter your name:\")
system.output "Your name is:" username
print "The username is:" username
"""
    parser(codee)
    print(Fore.CYAN + f"Variables: {variables}" + Style.RESET_ALL)