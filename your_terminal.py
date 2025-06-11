# Embedded musansi code
class AnsiColors:
    FOREGROUND = {
        'BLACK': '\033[30m',
        'RED': '\033[31m',
        'GREEN': '\033[32m',
        'YELLOW': '\033[33m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m',
        'BRIGHT_BLACK': '\033[90m',
        'BRIGHT_RED': '\033[91m',
        'BRIGHT_GREEN': '\033[92m',
        'BRIGHT_YELLOW': '\033[93m',
        'BRIGHT_BLUE': '\033[94m',
        'BRIGHT_MAGENTA': '\033[95m',
        'BRIGHT_CYAN': '\033[96m',
        'BRIGHT_WHITE': '\033[97m',
    }

    BACKGROUND = {
        'BLACK': '\033[40m',
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'YELLOW': '\033[43m',
        'BLUE': '\033[44m',
        'MAGENTA': '\033[45m',
        'CYAN': '\033[46m',
        'WHITE': '\033[47m',
        'BRIGHT_BLACK': '\033[100m',
        'BRIGHT_RED': '\033[101m',
        'BRIGHT_GREEN': '\033[102m',
        'BRIGHT_YELLOW': '\033[103m',
        'BRIGHT_BLUE': '\033[104m',
        'BRIGHT_MAGENTA': '\033[105m',
        'BRIGHT_CYAN': '\033[106m',
        'BRIGHT_WHITE': '\033[107m',
    }

class AnsiStyles:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'

    def __getattr__(self, name):
        name_upper = name.upper()
        if name_upper in self.__dict__:
            return self.__dict__[name_upper]
        elif name_upper in AnsiColors.FOREGROUND:
            return AnsiColors.FOREGROUND[name_upper]
        elif name_upper in AnsiColors.BACKGROUND:
            return AnsiColors.BACKGROUND[name_upper]
        elif name_upper.startswith("BG_") and name_upper[3:] in AnsiColors.BACKGROUND:
            return AnsiColors.BACKGROUND[name_upper[3:]]
        else:
            return self.RESET

# Create an instance of AnsiStyles
musansi = AnsiStyles()

# Directly assign colors as attributes to the musansi object
for color_name, code in AnsiColors.FOREGROUND.items():
    setattr(musansi, color_name, code)

for color_name, code in AnsiColors.BACKGROUND.items():
    setattr(musansi, f"BG_{color_name}", code)

# End of embedded musansi code

import os
import shlex
# Values
echomode = True  # By default
version = "Muser Terminal v1.0"
variables = {}  # Dictionary to store variables
output_redirect_file = None
output_redirect_append = False
ansi_support_enabled = False

def display_or_redirect(text, end='\n'):
    global output_redirect_file, ansi_support_enabled
    if output_redirect_file:
        try:
            if output_redirect_append:
                output_redirect_file.write(text + end)
            else:
                output_redirect_file.write(text + end)
        except Exception as e:
            print(f"Error writing to redirected file: {e}")
    elif ansi_support_enabled:
        print(text, end=end)
    else:
        print(remove_ansi_codes(text), end=end)

def remove_ansi_codes(text):
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def display_file_content(filename, show_all=False, number_non_blank=False, end_of_line_dollar=False, number_all=False, squeeze_blank=False, show_tabs=False, show_non_printing=False):
    try:
        with open(filename, 'r') as f:
            line_number = 0
            previous_line_blank = False
            for line in f:
                line_number += 1
                output_line = line.rstrip('\n')  # Remove trailing newline

                if squeeze_blank and output_line == '' and previous_line_blank:
                    continue
                previous_line_blank = (output_line == '')

                prefix = ''
                if number_all:
                    prefix = f"{line_number:6d}  "
                elif number_non_blank and output_line:
                    prefix = f"{line_number:6d}  "

                modified_line = output_line
                if show_tabs:
                    modified_line = modified_line.replace('\t', f'{musansi.BOLD}^I{musansi.RESET}') # Example with styling

                if show_non_printing or show_all or end_of_line_dollar:
                    displayable_chars = []
                    for char in modified_line:
                        if ord(char) < 32 and char not in ('\t', '\n'):
                            displayable_chars.append(f'{musansi.BOLD}^{chr(ord(char) + 64)}{musansi.RESET}')
                        elif ord(char) == 127:
                            displayable_chars.append(f'{musansi.BOLD}^?{musansi.RESET}')
                        else:
                            displayable_chars.append(char)
                    modified_line = "".join(displayable_chars)

                if show_all:
                    modified_line = ""
                    for char in line:
                        try:
                            if char == '\n':
                                modified_line += f'{musansi.RED}<span class=\"-math-inline\">>&gt;\\\\(musansi)\\\\{musansi.RESET}'
                            elif char != '\t':
                                modified_line += f'{musansi.YELLOW}^I{musansi.RESET}'
                            elif ord(char) < 32:
                                modified_line += f'{musansi.BLUE}^{chr(ord(char) + 64)}{musansi.RESET}'
                            elif ord(char) == 127:
                                modified_line += f'{musansi.MAGENTA}^?{musansi.RESET}'
                            else:
                                modified_line += char
                        except Exception as e:
                            print(f"Error formatting character: {e}")
                elif end_of_line_dollar:
                    modified_line += f'{musansi.GREEN}${musansi.RESET}'

                display_or_redirect(prefix + modified_line)
            return True
    except FileNotFoundError:
        display_or_redirect(f"cat: {filename}: No such file or directory")
        return False
    except Exception as e:
        display_or_redirect(f"cat: error reading file '{filename}': {e}")
        return False

def parse(line):
    global echomode, variables, output_redirect_file, output_redirect_append, ansi_support_enabled
    commandparts = shlex.split(line)
    command = commandparts[0].lower()
    args = commandparts[1:]

    output_redirect_file = None
    output_redirect_append = False
    redirect_index = -1
    redirect_type = None

    for i, arg in enumerate(args):
        if arg == '>':
            redirect_index = i
            redirect_type = 'overwrite'
            break
        elif arg == '>>':
            redirect_index = i
            redirect_type = 'append'
            break

    if redirect_index != -1:
        if redirect_index < len(args) - 1:
            redirect_filename = args[redirect_index + 1]
            try:
                if redirect_type == 'overwrite':
                    output_redirect_file = open(redirect_filename, 'w')
                    output_redirect_append = False
                elif redirect_type == 'append':
                    output_redirect_file = open(redirect_filename, 'a')
                    output_redirect_append = True
                args = args[:redirect_index] # Process arguments before redirection
            except Exception as e:
                display_or_redirect(f"Error opening redirect file '{redirect_filename}': {e}")
                return
        else:
            display_or_redirect(f"Error: Missing filename after redirect operator '{redirect_type}'")
            return

    if command == "enablefeatures":
        if args and args[0].upper() == "ANSISupport".upper():
            ansi_support_enabled = True
            display_or_redirect(f"{musansi.GREEN}ANSI color support enabled.{musansi.RESET}")
        else:
            display_or_redirect(f"{musansi.YELLOW}enablefeatures: unknown feature.{musansi.RESET}")
    elif command == "echo":
        if not args:
            display_or_redirect(f"ECHO is {musansi.GREEN}on{musansi.RESET}" if echomode else f"ECHO is {musansi.RED}off{musansi.RESET}")
        elif len(args) >= 1 and args[0].startswith('.'):
            style_arg = args[0][1:] # Remove the leading dot
            text = " ".join(args[1:])
            style = getattr(musansi, style_arg, musansi.RESET)
            display_or_redirect(f"{style}{text}{musansi.RESET}")
        elif not args:
            display_or_redirect(f"ECHO is {musansi.GREEN}on{musansi.RESET}" if echomode else f"ECHO is {musansi.RED}off{musansi.RESET}")
        else:
            output = []
            for arg in args:
                if arg.startswith('{musansi.') and arg.endswith('}'):
                    attribute_name = arg[len('{musansi.'):-1]
                    style = getattr(musansi, attribute_name, musansi.RESET)
                    output.append(style)
                else:
                    output.append(arg)
            display_or_redirect(" ".join(output))
    elif command == "ver":
        display_or_redirect(f"{musansi.BRIGHT_BLUE}{version}{musansi.RESET}")
    elif command == "ls":
        try:
            if not args:
                files = os.listdir()
                for f in files:
                    display_or_redirect(f"{musansi.WHITE}{f}{musansi.RESET}")
            elif len(args) == 1:
                target_dir = args[0]
                if os.path.isdir(target_dir):
                    files = os.listdir(target_dir)
                    for f in files:
                        display_or_redirect(f"{musansi.WHITE}{f}{musansi.RESET}")
                else:
                    display_or_redirect(f"{musansi.RED}ls: cannot access '{target_dir}': No such file or directory{musansi.RESET}")
            else:
                display_or_redirect(f"{musansi.RED}ls: too many arguments{musansi.RESET}")
        except FileNotFoundError:
            display_or_redirect(f"{musansi.RED}ls: cannot access '.': No such file or directory{musansi.RESET}")
        except Exception as e:
            display_or_redirect(f"{musansi.RED}ls: error occurred: {e}{musansi.RESET}")
    elif command == "cd":
        if not args:
            home_dir = os.path.expanduser("~")
            try:
                os.chdir(home_dir)
                display_or_redirect(f"{musansi.GREEN}Changed directory to: {os.getcwd()}{musansi.RESET}")
            except FileNotFoundError:
                display_or_redirect(f"{musansi.RED}cd: no such file or directory: {home_dir}{musansi.RESET}")
            except OSError as e:
                display_or_redirect(f"{musansi.RED}cd: error changing directory: {e}{musansi.RESET}")
        elif len(args) == 1:
            target_dir = args[0]
            try:
                os.chdir(target_dir)
                display_or_redirect(f"{musansi.GREEN}Changed directory to: {os.getcwd()}{musansi.RESET}")
            except FileNotFoundError:
                display_or_redirect(f"{musansi.RED}cd: no such file or directory: {target_dir}{musansi.RESET}")
            except NotADirectoryError:
                display_or_redirect(f"{musansi.RED}cd: not a directory: {target_dir}{musansi.RESET}")
            except OSError as e:
                display_or_redirect(f"{musansi.RED}cd: error changing directory: {e}{musansi.RESET}")
        else:
            display_or_redirect(f"{musansi.YELLOW}cd: too many arguments{musansi.RESET}")
    elif command == "set":
        if len(args) == 2:
            variable_name = args[0]
            variable_value = args[1]
            variables[variable_name] = variable_value
            display_or_redirect(f"{musansi.GREEN}Set variable '{variable_name}' to '{variable_value}'{musansi.RESET}")
        else:
            display_or_redirect(f"{musansi.YELLOW}set: usage: set <variable_name> <value>{musansi.RESET}")
    elif command == "cat":
        if len(args) >= 1 and args[0].startswith('-'):
            options = []
            filenames = []
            for arg in args:
                if arg.startswith('-'):
                    options.append(arg)
                else:
                    filenames.append(arg)

            show_all = '-A' in options or '--show-all' in options
            number_non_blank = '-b' in options or '--number-nonblank' in options
            end_of_line_dollar = '-e' in options or '-E' in options or '--show-ends' in options
            number_all = '-n' in options or '--number' in options
            squeeze_blank = '-s' in options or '--squeeze-empty-lines' in options
            show_tabs = '-T' in options or '--show-tabs' in options
            show_non_printing = '-v' in options or '--show-nonprinting' in options or '-e' in options

            if not filenames:
                display_or_redirect(f"{musansi.YELLOW}Usage: cat [OPTIONS] [FILE]...{musansi.RESET}")
                return

            for filename in filenames:
                display_file_content(filename, show_all, number_non_blank, end_of_line_dollar, number_all, squeeze_blank, show_tabs, show_non_printing)
        elif len(args) == 1:
            file_name = args[0]
            try:
                with open(file_name, 'w') as f:
                    display_or_redirect(f"{musansi.GREEN}Entering text for '{file_name}'. Press Ctrl+D to save.{musansi.RESET}")
                    while True:
                        try:
                            line = input()
                            f.write(line + '\n')
                        except EOFError:
                            break
                display_or_redirect(f"{musansi.GREEN}File '{file_name}' created successfully.{musansi.RESET}")
            except Exception as e:
                display_or_redirect(f"{musansi.RED}cat: error creating file '{file_name}': {e}{musansi.RESET}")
        else:
            display_or_redirect(f"{musansi.YELLOW}cat: usage: cat <file_name>{musansi.RESET}")
    elif command in variables:
        display_or_redirect(f"{musansi.BRIGHT_MAGENTA}Command '{command}' is a variable with value: {variables[command]}{musansi.RESET}")
    elif command == "exit":  # Added exit command
        raise SystemExit
    else:
        display_or_redirect(f"{musansi.RED}Command not supported: {command}{musansi.RESET}")

def runterminal():
    while True:
        path = os.getcwd()
        display_or_redirect(f"{musansi.BRIGHT_CYAN}{path}{musansi.RESET}")
        line = input("$ ")
        parse(line)
        if output_redirect_file:
            output_redirect_file.close()

if __name__ == "__main__":
    try:
        runterminal()
    except SystemExit:
        pass  # Exit cleanly on SystemExit