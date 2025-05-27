#!/usr/bin/env python3
# Advanced Python Logging - Developed by acidvegas in Python (https://git.acid.vegas/apv)
# apv.py

import gzip
import json
import logging
import logging.handlers
import os
import socket
import sys


class LogColors:
    '''ANSI color codes for log messages'''

    NOTSET    = '\033[97m'         # White text
    DEBUG     = '\033[96m'         # Cyan
    INFO      = '\033[92m'         # Green
    WARNING   = '\033[93m'         # Yellow
    ERROR     = '\033[91m'         # Red
    CRITICAL  = '\033[97m\033[41m' # White on Red
    FATAL     = '\033[97m\033[41m' # Same as CRITICAL
    DATE      = '\033[90m'         # Dark Grey
    MODULE    = '\033[95m'         # Pink
    FUNCTION  = '\033[94m'         # Blue
    LINE      = '\033[33m'         # Orange
    RESET     = '\033[0m'
    SEPARATOR = '\033[90m'         # Dark Grey


class ConsoleFormatter(logging.Formatter):
    '''A formatter for the consolethat supports colored output'''
    
    def __init__(self, datefmt: str = None, details: bool = False):
        super().__init__(datefmt=datefmt)
        self.details = details


    def format(self, record: logging.LogRecord) -> str:
        '''
        Format a log record for the console
        
        :param record: The log record to format
        '''

        # Get the color for the log level
        color = getattr(LogColors, record.levelname, LogColors.RESET)
        
        # Format the log level
        log_level = f'{color}{record.levelname:<8}{LogColors.RESET}'

        # Get the log message
        message = record.getMessage()

        # Format the timestamp
        asctime = f'{LogColors.DATE}{self.formatTime(record, self.datefmt)}'

        # Get the separator
        separator = f'{LogColors.SEPARATOR} ┃ {LogColors.RESET}'
        details   = f'{LogColors.MODULE}{record.module}{separator}{LogColors.FUNCTION}{record.funcName}{separator}{LogColors.LINE}{record.lineno}{separator}' if self.details else ''
        
        return f'{asctime}{separator}{log_level}{separator}{details}{message}'


class JsonFormatter(logging.Formatter):
    '''Formatter for JSON output'''
    
    def __init__(self, datefmt: str = None):
        super().__init__(datefmt=datefmt)


    def format(self, record: logging.LogRecord) -> str:
        '''
        Format a log record for JSON output
        
        :param record: The log record to format
        '''

        # Create a dictionary to store the log record
        log_dict = {
            '@timestamp'    : self.formatTime(record, self.datefmt),
            'level'        : record.levelname,
            'message'      : record.getMessage(),
            'process_id'   : record.process,
            'process_name' : record.processName,
            'thread_id'    : record.thread,
            'thread_name'  : record.threadName,
            'logger_name'  : record.name,
            'filename'     : record.filename,
            'line_number'  : record.lineno,
            'function'     : record.funcName,
            'module'       : record.module,
            'hostname'     : socket.gethostname()
        }

        # Add the exception if it exists
        if record.exc_info:
            log_dict['exception'] = self.formatException(record.exc_info)

        # Add any custom attributes that start with an underscore
        custom_attrs = {k: v for k, v in record.__dict__.items() if k.startswith('_') and not k.startswith('__')}
        log_dict.update(custom_attrs)

        return json.dumps(log_dict)


class GZipRotatingFileHandler(logging.handlers.RotatingFileHandler):
    '''RotatingFileHandler that compresses rotated log files'''
    
    def rotation_filename(self, default_name: str) -> str:
        return default_name + '.gz'

    def rotate(self, source: str, dest: str):
        with open(source, 'rb') as src, gzip.open(dest, 'wb') as dst:
            dst.write(src.read())


class LoggerSetup:
    def __init__(self, level: str = 'INFO', date_format: str = '%Y-%m-%d %H:%M:%S', log_to_disk: bool = False, max_log_size: int = 10*1024*1024, max_backups: int = 7, log_file_name: str = 'app', json_log: bool = False, show_details: bool = False, compress_backups: bool = False):
        '''
        Initialize the LoggerSetup with provided parameters
        
        :param level: The logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        :param date_format: The date format for log messages
        :param log_to_disk: Whether to log to disk
        :param max_log_size: The maximum size of log files before rotation
        :param max_backups: The maximum number of backup log files to keep
        :param log_file_name: The base name of the log file
        :param json_log: Whether to log in JSON format
        :param show_details: Whether to show detailed log messages
        :param compress_backups: Whether to compress old log files using gzip
        '''

        self.level            = level
        self.date_format      = date_format
        self.log_to_disk      = log_to_disk
        self.max_log_size     = max_log_size
        self.max_backups      = max_backups
        self.log_file_name    = log_file_name
        self.json_log         = json_log
        self.show_details     = show_details
        self.compress_backups = compress_backups


    def setup(self):
        '''Set up logging with various handlers and options'''

        # Clear existing handlers
        logging.getLogger().handlers.clear()
        logging.getLogger().setLevel(logging.DEBUG)

        # Convert the level string to a logging level object
        level_num = getattr(logging, self.level.upper(), logging.INFO)

        # Setup console handler
        self.setup_console_handler(level_num)

        # Setup file handler if enabled
        if self.log_to_disk:
            self.setup_file_handler(level_num)


    def setup_console_handler(self, level_num: int):
        '''
        Set up the console handler
        
        :param level_num: The logging level number
        '''

        # Create the console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level_num)
        
        # Create the formatter
        formatter = JsonFormatter(datefmt=self.date_format) if self.json_log else ConsoleFormatter(datefmt=self.date_format, details=self.show_details)
        console_handler.setFormatter(formatter)
        
        # Add the handler to the root logger
        logging.getLogger().addHandler(console_handler)


    def setup_file_handler(self, level_num: int):
        '''
        Set up the file handler
        
        :param level_num: The logging level number
        '''

        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(sys.path[0], 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Set up log file path
        file_extension = '.json' if self.json_log else '.log'
        log_file_path  = os.path.join(logs_dir, f'{self.log_file_name}{file_extension}')

        # Create the rotating file handler
        handler_class = GZipRotatingFileHandler if self.compress_backups else logging.handlers.RotatingFileHandler
        file_handler  = handler_class(log_file_path, maxBytes=self.max_log_size, backupCount=self.max_backups)
        file_handler.setLevel(level_num)

        # Set up the appropriate formatter
        formatter = JsonFormatter(datefmt=self.date_format) if self.json_log else logging.Formatter(fmt='%(asctime)s ┃ %(levelname)-8s ┃ %(module)s ┃ %(funcName)s ┃ %(lineno)d ┃ %(message)s', datefmt=self.date_format)
        file_handler.setFormatter(formatter)

        logging.getLogger().addHandler(file_handler)


def setup_logging(**kwargs):
    '''Set up logging with various handlers and options'''

    # Create a LoggerSetup instance with the provided keyword arguments
    logger_setup = LoggerSetup(**kwargs)

    # Set up the logging system
    logger_setup.setup() 