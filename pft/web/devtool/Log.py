import datetime
from typing import Literal

class Log:
    
    RESET = "\033[0m"
    BLACK   = "\033[0;30m"  # BLACK
    RED     = "\033[0;31m"  # RED
    GREEN   = "\033[0;32m"  # GREEN
    YELLOW  = "\033[0;33m"  # YELLOW
    BLUE    = "\033[0;34m"  # BLUE
    PURPLE  = "\033[0;35m"  # PURPLE
    CYAN    = "\033[0;36m"  # CYAN
    WHITE   = "\033[0;37m"  # WHITE
    
    def color(*text: str, color=WHITE):
        all_text = ""
        for t in text:
            all_text+=str(t)
        return color + all_text + Log.RESET
    
    def print(*values: object, sep: str | None = " ", end: str | None = "\n", file = None, flush: Literal[False] = False, style = WHITE):
        print(f"Server    - - [{Log.color(datetime.datetime.now().strftime('%d/%b/%Y %H:%M:%S'))}] "+Log.color(*values, color=style))