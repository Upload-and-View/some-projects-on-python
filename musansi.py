# musansi.py

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