#!/usr/bin/env python3
# Advanced Python Logging - Developed by acidvegas in Python (https://git.acid.vegas/apv)
# apv.py

import gzip
import json
import logging
import logging.handlers
import os
import socket


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


class GZipRotatingFileHandler(logging.handlers.RotatingFileHandler):
    '''RotatingFileHandler that compresses old log files using gzip.'''

    def doRollover(self):
        '''Compress old log files using gzip.'''

        super().doRollover()
        if self.backupCount > 0:
            for i in range(self.backupCount, 0, -1):
                sfn = f'{self.baseFilename}.{i}'
                if os.path.exists(sfn):
                    with open(sfn, 'rb') as f_in:
                        with gzip.open(f'{sfn}.gz', 'wb') as f_out:
                            f_out.writelines(f_in)
                    os.remove(sfn)


class LoggerSetup:
    def __init__(self, level='INFO', date_format='%Y-%m-%d %H:%M:%S',
                 log_to_disk=False, max_log_size=10*1024*1024,
                 max_backups=7, log_file_name='app', json_log=False,
                 ecs_log=False, show_details=False, compress_backups=False,
                 enable_graylog=False, graylog_host=None, graylog_port=None,
                 enable_cloudwatch=False, cloudwatch_group_name=None, cloudwatch_stream_name=None):
        '''
        Initialize the LoggerSetup with provided parameters.
        
        :param level: The logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        :param date_format: The date format for log messages.
        :param log_to_disk: Whether to log to disk.
        :param max_log_size: The maximum size of log files before rotation.
        :param max_backups: The maximum number of backup log files to keep.
        :param log_file_name: The base name of the log file.
        :param json_log: Whether to log in JSON format.
        :param show_details: Whether to show detailed log messages.
        :param compress_backups: Whether to compress old log files using gzip.
        :param enable_graylog: Whether to enable Graylog logging.
        :param graylog_host: The Graylog host.
        :param graylog_port: The Graylog port.
        :param enable_cloudwatch: Whether to enable CloudWatch logging.
        :param cloudwatch_group_name: The CloudWatch log group name.
        :param cloudwatch_stream_name: The CloudWatch log stream name.
        '''

        self.level                  = level
        self.date_format            = date_format
        self.log_to_disk            = log_to_disk
        self.max_log_size           = max_log_size
        self.max_backups            = max_backups
        self.log_file_name          = log_file_name
        self.json_log               = json_log
        self.ecs_log                = ecs_log
        self.show_details           = show_details
        self.compress_backups       = compress_backups
        self.enable_graylog         = enable_graylog
        self.graylog_host           = graylog_host
        self.graylog_port           = graylog_port
        self.enable_cloudwatch      = enable_cloudwatch
        self.cloudwatch_group_name  = cloudwatch_group_name
        self.cloudwatch_stream_name = cloudwatch_stream_name


    def setup(self):
        '''Set up logging with various handlers and options.'''

        # Clear existing handlers
        logging.getLogger().handlers.clear()
        logging.getLogger().setLevel(logging.DEBUG)  # Capture all logs at the root level

        # Convert the level string to a logging level object
        level_num = getattr(logging, self.level.upper(), logging.INFO)

        self.setup_console_handler(level_num)

        if self.log_to_disk:
            self.setup_file_handler(level_num)

        if self.enable_graylog:
            self.setup_graylog_handler(level_num)

        if self.enable_cloudwatch:
            self.setup_cloudwatch_handler(level_num)


    def setup_console_handler(self, level_num: int):
        '''
        Set up the console handler with colored output.
        
        :param level_num: The logging level number.
        '''

        # Define the colored formatter
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
                    module    = record.module
                    line_no   = record.lineno
                    func_name = record.funcName
                    formatted = (
                        f'{LogColors.DATE}{asctime}{LogColors.RESET}'
                        f'{separator}'
                        f'{color}{log_level:<8}{LogColors.RESET}'
                        f'{separator}'
                        f'{LogColors.MODULE}{module}{LogColors.RESET}'
                        f'{separator}'
                        f'{LogColors.FUNCTION}{func_name}{LogColors.RESET}'
                        f'{separator}'
                        f'{LogColors.LINE}{line_no}{LogColors.RESET}'
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

        # Create console handler with colored output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level_num)
        console_formatter = ColoredFormatter(datefmt=self.date_format, show_details=self.show_details)
        console_handler.setFormatter(console_formatter)
        logging.getLogger().addHandler(console_handler)


    def setup_file_handler(self, level_num: int):
        '''
        Set up the file handler for logging to disk.
        
        :param level_num: The logging level number.
        '''

        # Create 'logs' directory if it doesn't exist
        logs_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Use the specified log file name and set extension based on json_log
        file_extension = '.json' if self.json_log else '.log'
        log_file_path = os.path.join(logs_dir, f'{self.log_file_name}{file_extension}')

        # Create the rotating file handler
        if self.compress_backups:
            file_handler = GZipRotatingFileHandler(log_file_path, maxBytes=self.max_log_size, backupCount=self.max_backups)
        else:
            file_handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=self.max_log_size, backupCount=self.max_backups)
        file_handler.setLevel(level_num)

        if self.ecs_log:
            try:
                import ecs_logging
            except ImportError:
                raise ImportError("The 'ecs-logging' library is required for ECS logging. Install it with 'pip install ecs-logging'.")
            file_formatter = ecs_logging.StdlibFormatter()
        elif self.json_log:
            # Create the JSON formatter
            class JsonFormatter(logging.Formatter):
                def format(self, record):
                    log_record = {
                        'time'        : self.formatTime(record, self.datefmt),
                        'level'       : record.levelname,
                        'module'      : record.module,
                        'function'    : record.funcName,
                        'line'        : record.lineno,
                        'message'     : record.getMessage(),
                        'name'        : record.name,
                        'filename'    : record.filename,
                        'threadName'  : record.threadName,
                        'processName' : record.processName,
                    }
                    return json.dumps(log_record)
            file_formatter = JsonFormatter(datefmt=self.date_format)
        else:
            file_formatter = logging.Formatter(fmt='%(asctime)s ┃ %(levelname)-8s ┃ %(module)s ┃ %(funcName)s ┃ %(lineno)d ┃ %(message)s', datefmt=self.date_format)

        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)


    def setup_graylog_handler(self, level_num: int):
        '''
        Set up the Graylog handler.
        
        :param level_num: The logging level number.
        '''

        graylog_host = self.graylog_host
        graylog_port = self.graylog_port
        if graylog_host is None or graylog_port is None:
            logging.error('Graylog host and port must be specified for Graylog handler.')
            return

        class GraylogHandler(logging.Handler):
            def __init__(self, graylog_host, graylog_port):
                super().__init__()
                self.graylog_host = graylog_host
                self.graylog_port = graylog_port
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                # Mapping from Python logging levels to Graylog (syslog) levels
                self.level_mapping = {
                    logging.CRITICAL : 2, # Critical
                    logging.ERROR    : 3, # Error
                    logging.WARNING  : 4, # Warning
                    logging.INFO     : 6, # Informational
                    logging.DEBUG    : 7, # Debug
                    logging.NOTSET   : 7  # Default to Debug
                }

            def emit(self, record):
                try:
                    log_entry = self.format(record)
                    graylog_level = self.level_mapping.get(record.levelno, 7)  # Default to Debug
                    gelf_message = {
                        'version'       : '1.1',
                        'host'          : socket.gethostname(),
                        'short_message' : record.getMessage(),
                        'full_message'  : log_entry,
                        'timestamp'     : record.created,
                        'level'         : graylog_level,
                        '_logger_name'  : record.name,
                        '_file'         : record.pathname,
                        '_line'         : record.lineno,
                        '_function'     : record.funcName,
                        '_module'       : record.module,
                    }
                    gelf_json = json.dumps(gelf_message).encode('utf-8')
                    self.sock.sendto(gelf_json, (self.graylog_host, self.graylog_port))
                except Exception:
                    self.handleError(record)

        graylog_handler = GraylogHandler(graylog_host, graylog_port)
        graylog_handler.setLevel(level_num)

        graylog_formatter = logging.Formatter(fmt='%(message)s')
        graylog_handler.setFormatter(graylog_formatter)
        logging.getLogger().addHandler(graylog_handler)


    def setup_cloudwatch_handler(self, level_num: int):
        '''
        Set up the CloudWatch handler.
        
        :param level_num: The logging level number.
        '''

        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise ImportError('boto3 is required for CloudWatch logging. (pip install boto3)')

        log_group_name = self.cloudwatch_group_name
        log_stream_name = self.cloudwatch_stream_name
        if not log_group_name or not log_stream_name:
            logging.error('CloudWatch log group and log stream must be specified for CloudWatch handler.')
            return

        class CloudWatchHandler(logging.Handler):
            def __init__(self, log_group_name, log_stream_name):
                super().__init__()
                self.log_group_name = log_group_name
                self.log_stream_name = log_stream_name
                self.client = boto3.client('logs')

                # Create log group if it doesn't exist
                try:
                    self.client.create_log_group(logGroupName=self.log_group_name)
                except ClientError as e:
                    if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                        raise e

                # Create log stream if it doesn't exist
                try:
                    self.client.create_log_stream(logGroupName=self.log_group_name, logStreamName=self.log_stream_name)
                except ClientError as e:
                    if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                        raise e

            def _get_sequence_token(self):
                try:
                    response = self.client.describe_log_streams(
                        logGroupName=self.log_group_name,
                        logStreamNamePrefix=self.log_stream_name,
                        limit=1
                    )
                    log_streams = response.get('logStreams', [])
                    if log_streams:
                        return log_streams[0].get('uploadSequenceToken')
                    else:
                        return None
                except Exception:
                    return None

            def emit(self, record):
                try:
                    log_entry = self.format(record)
                    timestamp = int(record.created * 1000)
                    event = {
                        'timestamp': timestamp,
                        'message': log_entry
                    }
                    sequence_token = self._get_sequence_token()
                    kwargs = {
                        'logGroupName': self.log_group_name,
                        'logStreamName': self.log_stream_name,
                        'logEvents': [event]
                    }
                    if sequence_token:
                        kwargs['sequenceToken'] = sequence_token
                    self.client.put_log_events(**kwargs)
                except Exception:
                    self.handleError(record)

        cloudwatch_handler = CloudWatchHandler(log_group_name, log_stream_name)
        cloudwatch_handler.setLevel(level_num)
        
        # Log as JSON
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'time'        : self.formatTime(record, self.datefmt),
                    'level'       : record.levelname,
                    'module'      : record.module,
                    'function'    : record.funcName,
                    'line'        : record.lineno,
                    'message'     : record.getMessage(),
                    'name'        : record.name,
                    'filename'    : record.filename,
                    'threadName'  : record.threadName,
                    'processName' : record.processName,
                }
                return json.dumps(log_record)
            
        cloudwatch_formatter = JsonFormatter(datefmt=self.date_format)
        cloudwatch_handler.setFormatter(cloudwatch_formatter)
        logging.getLogger().addHandler(cloudwatch_handler)



def setup_logging(**kwargs):
    '''Set up logging with various handlers and options.'''

    logger_setup = LoggerSetup(**kwargs)
    logger_setup.setup()