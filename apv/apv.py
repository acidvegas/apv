#!/usr/bin/env python3
# Advanced Python Logging - Developed by acidvegas in Python (https://git.acid.vegas/apv)
# apv.py

import logging
import logging.handlers

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
        '''Set up the console handler.'''
        try:
            from apv.plugins.console import setup_console_handler
            setup_console_handler(level_num, self.date_format, self.show_details)
        except ImportError:
            logging.error('Failed to import console handler')


    def setup_file_handler(self, level_num: int):
        '''Set up the file handler.'''
        try:
            from apv.plugins.file import setup_file_handler
            setup_file_handler(
                level_num=level_num,
                log_to_disk=self.log_to_disk,
                max_log_size=self.max_log_size,
                max_backups=self.max_backups,
                log_file_name=self.log_file_name,
                json_log=self.json_log,
                ecs_log=self.ecs_log,
                date_format=self.date_format,
                compress_backups=self.compress_backups
            )
        except ImportError:
            logging.error('Failed to import file handler')


    def setup_graylog_handler(self, level_num: int):
        '''
        Set up the Graylog handler.
        
        :param level_num: The logging level number.
        '''

        try:
            from apv.plugins.graylog import setup_graylog_handler
            setup_graylog_handler(level_num, self.graylog_host, self.graylog_port)
        except ImportError:
            logging.error('Failed to import Graylog handler')


    def setup_cloudwatch_handler(self, level_num: int):
        '''
        Set up the CloudWatch handler.
        
        :param level_num: The logging level number.
        '''

        try:
            from apv.plugins.cloudwatch import setup_cloudwatch_handler
            setup_cloudwatch_handler(
                level_num,
                self.cloudwatch_group_name,
                self.cloudwatch_stream_name,
                self.date_format
            )
        except ImportError:
            logging.error('Failed to import CloudWatch handler')



def setup_logging(**kwargs):
    '''Set up logging with various handlers and options.'''

    logger_setup = LoggerSetup(**kwargs)
    logger_setup.setup()