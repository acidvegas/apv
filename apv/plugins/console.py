import logging

class LogColors:
    '''ANSI color codes for log messages.'''
    RESET     = '\033[0m'
    DATE      = '\033[90m'         # Dark Grey
    DEBUG     = '\033[96m'         # Cyan
    INFO      = '\033[92m'         # Green
    WARNING   = '\033[93m'         # Yellow
    ERROR     = '\033[91m'         # Red
    CRITICAL  = '\033[97m\033[41m' # White on Red
    FATAL     = '\033[97m\033[41m' # Same as CRITICAL
    NOTSET    = '\033[97m'         # White text
    SEPARATOR = '\033[90m'         # Dark Grey
    MODULE    = '\033[95m'         # Pink
    FUNCTION  = '\033[94m'         # Blue
    LINE      = '\033[33m'         # Orange

class ColoredFormatter(logging.Formatter):
    def __init__(self, datefmt=None, show_details=False):
        super().__init__(datefmt=datefmt)
        self.show_details = show_details
        self.LEVEL_COLORS = {
            'NOTSET'   : LogColors.NOTSET,
            'DEBUG'    : LogColors.DEBUG,
            'INFO'     : LogColors.INFO,
            'WARNING'  : LogColors.WARNING,
            'ERROR'    : LogColors.ERROR,
            'CRITICAL' : LogColors.CRITICAL,
            'FATAL'    : LogColors.FATAL
        }

    def format(self, record):
        log_level = record.levelname
        message   = record.getMessage()
        asctime   = self.formatTime(record, self.datefmt)
        color     = self.LEVEL_COLORS.get(log_level, LogColors.RESET)
        separator = f'{LogColors.SEPARATOR} ┃ {LogColors.RESET}'
        
        if self.show_details:
            formatted = (
                f'{LogColors.DATE}{asctime}{LogColors.RESET}'
                f'{separator}'
                f'{color}{log_level:<8}{LogColors.RESET}'
                f'{separator}'
                f'{LogColors.MODULE}{record.module}{LogColors.RESET}'
                f'{separator}'
                f'{LogColors.FUNCTION}{record.funcName}{LogColors.RESET}'
                f'{separator}'
                f'{LogColors.LINE}{record.lineno}{LogColors.RESET}'
                f'{separator}'
                f'{message}'
            )
        else:
            formatted = (
                f'{LogColors.DATE}{asctime}{LogColors.RESET}'
                f'{separator}'
                f'{color}{log_level:<8}{LogColors.RESET}'
                f'{separator}'
                f'{message}'
            )
        return formatted

def setup_console_handler(level_num: int, date_format: str, show_details: bool):
    '''Set up the console handler with colored output.'''
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level_num)
    console_formatter = ColoredFormatter(datefmt=date_format, show_details=show_details)
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler) 