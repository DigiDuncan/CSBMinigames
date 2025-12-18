class ANSI:
    # C0 control codes
    BELL = "\a"
    BACKSPACE = "\b"
    TAB = "\t"
    LINE_FEED = "\n"
    NEW_LINE = LINE_FEED
    FORM_FEED = "\f"
    CARRAGE_RETURN = "\r"
    ESCAPE = "\033"
    # ! C1 control codes skipped
    # CSI commands (1)
    CURSOR_UP = ESCAPE + "[A"
    CUU = CURSOR_UP
    @classmethod
    def CURSOR_UP_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}A"
    CUU_N = CURSOR_UP_N

    CURSOR_DOWN = ESCAPE + "[B"
    CUD = CURSOR_DOWN
    @classmethod
    def CURSOR_DOWN_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}B"
    CUD_N = CURSOR_DOWN_N

    CURSOR_FORWARD = ESCAPE + "[C"
    CUF = CURSOR_FORWARD
    @classmethod
    def CURSOR_FORWARD_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}C"
    CUF_N = CURSOR_FORWARD_N

    CURSOR_BACK = ESCAPE + "[D"
    CUB = CURSOR_BACK
    @classmethod
    def CURSOR_BACK_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}D"
    CUB_N = CURSOR_BACK_N

    CURSOR_NEXT_LINE = ESCAPE + "[E"
    CNL = CURSOR_NEXT_LINE
    @classmethod
    def CURSOR_NEXT_LINE_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}E"
    CNL_N = CURSOR_NEXT_LINE_N

    CURSOR_PREVIOUS_LINE = ESCAPE + "[F"
    CPL = CURSOR_PREVIOUS_LINE
    @classmethod
    def CURSOR_PREVIOUS_LINE_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}F"
    CPL_N = CURSOR_PREVIOUS_LINE_N

    CURSOR_HORIZONTAL_ABSOLUTE = ESCAPE + "[G"
    CHA = CURSOR_HORIZONTAL_ABSOLUTE
    @classmethod
    def CURSOR_HORIZONTAL_ABSOLUTE_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}G"
    CHA_N = CURSOR_HORIZONTAL_ABSOLUTE_N

    CURSOR_POSITION = ESCAPE + "[H"
    CUP = CURSOR_POSITION
    @classmethod
    def CURSOR_POSITION_NM(cls, n: int = 1, m: int = 1): return cls.ESCAPE + f"[{n};{m}H"
    CUP_NM = CURSOR_POSITION_NM

    ERASE_IN_DISPLAY = ESCAPE + "[J"
    CLEAR = ESCAPE + "[2J" + CURSOR_POSITION
    ED = ERASE_IN_DISPLAY
    @classmethod
    def ERASE_IN_DISPLAY_N(cls, n: int = 0): return cls.ESCAPE + f"[{n}J"
    ED_N = ERASE_IN_DISPLAY_N

    ERASE_IN_LINE = ESCAPE + "[K"
    EL = ERASE_IN_LINE
    @classmethod
    def ERASE_IN_LINE_N(cls, n: int = 0): return cls.ESCAPE + f"[{n}K"
    EL_N = ERASE_IN_LINE_N

    SCROLL_UP = ESCAPE + "[S"
    SU = SCROLL_UP
    @classmethod
    def SCROLL_UP_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}S"
    SU_N = SCROLL_UP_N

    SCROLL_DOWN = ESCAPE + "[T"
    SD = SCROLL_DOWN
    @classmethod
    def SCROLL_DOWN_N(cls, n: int = 1): return cls.ESCAPE + f"[{n}T"
    SD_N = SCROLL_DOWN_N

    HORIZONTAL_VERTICAL_POSITION = ESCAPE + "[f"
    HVP = HORIZONTAL_VERTICAL_POSITION
    @classmethod
    def HORIZONTAL_VERTICAL_POSITION_NM(cls, n: int = 1, m: int = 1): return cls.ESCAPE + f"[{n};{m}f"
    HVP_NM = HORIZONTAL_VERTICAL_POSITION_NM

    AUX_PORT_ON = ESCAPE + "[5i"
    AUX_PORT_OFF = ESCAPE + "[4i"
    DEVICE_STATUS_REPORT = ESCAPE + "[6n"
    DSR = DEVICE_STATUS_REPORT

    # Select Graphic Rendition
    @classmethod
    def SELECT_GRAPHIC_RENDITION(cls, *n: int): return cls.ESCAPE + "[" + ";".join(str(c) for c in n) + "m"
    SGR = SELECT_GRAPHIC_RENDITION
    RESET = ESCAPE + "[0m"

    BOLD = ESCAPE + "[1m"
    NORMAL = ESCAPE + "[22m"
    FAINT = ESCAPE + "[2m"

    ITALIC = ESCAPE + "[3m"
    NOT_ITALIC = ESCAPE + "[23m"

    SLOW_BLINK = ESCAPE + "[5m"
    RAPID_BLINK = ESCAPE + "[6m"
    NOT_BLINKING = ESCAPE + "[25m"

    CONCEAL = ESCAPE + "[8m"
    REVEAL = ESCAPE + "[28m"

    STRIKETHROUGH = ESCAPE + "[9m"
    NO_STRIKETHROUGH = ESCAPE + "[29m"

    PROPORTIONAL_SPACING = ESCAPE + "[26m"
    NO_PROPORTIONAL_SPACING = ESCAPE + "[50m"

    FRAMED = ESCAPE + "[51m"
    ENCIRCLED = ESCAPE + "[52m"
    OVERLINED = ESCAPE + "[53m"
    NOT_FRAMED_OR_ENCIRCLED = ESCAPE + "[54m"
    NOT_OVERLINED = ESCAPE + "[55m"

    LINE_RIGHT = ESCAPE + "[60m"
    DOUBLE_LINE_RIGHT = ESCAPE + "[61m"
    LINE_LEFT = ESCAPE + "[62m"
    DOUBLE_LINE_LEFT = ESCAPE + "[63m"
    STRESS_MARKING = ESCAPE + "[64m"
    NO_LINE_OR_STRESS_MARKING = ESCAPE + "[65m"
    SUPERSCRIPT = ESCAPE + "[73m"
    SUBSCRIPT = ESCAPE + "[74m"
    REGULARSCRIPT = ESCAPE + "[75m"

    REVERSE_COLORS = ESCAPE + "[7m"
    NOT_REVERSE_COLORS = ESCAPE + "[27m"

    FOREGROUND_DEFAULT = ESCAPE + "[39m"
    FOREGROUND_BLACK = ESCAPE + "[30m"
    FOREGROUND_RED = ESCAPE + "[31m"
    FOREGROUND_GREEN = ESCAPE + "[32m"
    FOREGROUND_BLUE = ESCAPE + "[33m"
    FOREGROUND_MAGENTA = ESCAPE + "[34m"
    FOREGROUND_YELLOW = ESCAPE + "[35"
    FOREGROUND_CYAN = ESCAPE + "[36m"
    FOREGROUND_WHITE = ESCAPE + "[37m"
    FOREGROUND_BRIGHT_BLACK = ESCAPE + "[90m"
    FOREGROUND_BRIGHT_RED = ESCAPE + "[91m"
    FOREGROUND_BRIGHT_GREEN = ESCAPE + "[92m"
    FOREGROUND_BRIGHT_BLUE = ESCAPE + "[93m"
    FOREGROUND_BRIGHT_MAGENTA = ESCAPE + "[94m"
    FOREGROUND_BRIGHT_YELLOW = ESCAPE + "[95"
    FOREGROUND_BRIGHT_CYAN = ESCAPE + "[96m"
    FOREGROUND_BRIGHT_WHITE = ESCAPE + "[97m"
    @classmethod
    def FOREGROUND_N(cls, n: int = 0): return cls.ESCAPE + f"[38;5;{n}m"
    @classmethod
    def FOREGROUND_RGB(cls, r: int = 0, g: int = 0, b: int = 0): return cls.ESCAPE + f"[38;2;{r};{g};{b}m"

    BACKGROUND_DEFAULT = ESCAPE + "[49m"
    BACKGROUND_BLACK = ESCAPE + "[40m"
    BACKGROUND_RED = ESCAPE + "[41m"
    BACKGROUND_GREEN = ESCAPE + "[42m"
    BACKGROUND_BLUE = ESCAPE + "[43m"
    BACKGROUND_MAGENTA = ESCAPE + "[44m"
    BACKGROUND_YELLOW = ESCAPE + "[45"
    BACKGROUND_CYAN = ESCAPE + "[46m"
    BACKGROUND_WHITE = ESCAPE + "[47m"
    BACKGROUND_BRIGHT_BLACK = ESCAPE + "[100m"
    BACKGROUND_BRIGHT_RED = ESCAPE + "[101m"
    BACKGROUND_BRIGHT_GREEN = ESCAPE + "[102m"
    BACKGROUND_BRIGHT_BLUE = ESCAPE + "[103m"
    BACKGROUND_BRIGHT_MAGENTA = ESCAPE + "[104m"
    BACKGROUND_BRIGHT_YELLOW = ESCAPE + "[105"
    BACKGROUND_BRIGHT_CYAN = ESCAPE + "[106m"
    BACKGROUND_BRIGHT_WHITE = ESCAPE + "[107m"
    @classmethod
    def BACKGROUND_N(cls, n: int = 0): return cls.ESCAPE + f"[48;5;{n}m"
    @classmethod
    def BACKGROUND_RGB(cls, r: int = 0, g: int = 0, b: int = 0): return cls.ESCAPE + f"[48;2;{r};{g};{b}m"

    UNDERLINE = ESCAPE + "[4m"
    DOUBLE_UNDERLINE = ESCAPE + "[21"
    NOT_UNDERLINE = ESCAPE + "[24"
    UNDERLINE_DEFAULT = ESCAPE + "[59m"
    @classmethod
    def UNDERLINE_COLOR_N(cls, n: int = 0): return cls.ESCAPE + f"[58;5;{n}"
    @classmethod
    def UNDERLINE_COLOR_RGB(cls, r: int = 0, g: int = 0, b: int = 0): return cls.ESCAPE + f"[58;2;{r};{g};{b}m"

    DEFAULT_FONT = ESCAPE + "[10m"
    @classmethod
    def FONT_N(cls, n: int = 0): return cls.ESCAPE + f"[{n+10}m"

    @classmethod
    def RENDER(cls, code: str, text: str):
        return f"{code}{text}{cls.RESET}"

    # ! Fs control codes skipped
    # ! Fp control codes skipped
    # ! nF control codes skipped