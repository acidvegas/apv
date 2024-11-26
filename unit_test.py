#! /usr/bin/env python3
# Advanced Python Logging - Developed by acidvegas in Python (https://git.acid.vegas/apv)
# unittest.py

import logging
import random
import time

# prevent bytecode files (.pyc) from being written
from sys import dont_write_bytecode
dont_write_bytecode = True

import apv

# Test console logging with custom date format
apv.setup_logging(level='DEBUG', date_format='%H:%M:%S')
logging.debug('Testing debug message in console.')
logging.info('Testing info message in console.')
logging.warning('Testing warning message in console.')
logging.error('Testing error message in console.')
logging.critical('Testing critical message in console.')

print()

# Test console logging with details
time.sleep(2)
apv.setup_logging(level='DEBUG', date_format='%Y-%m-%d %H:%M:%S', show_details=True)
logging.debug('Testing debug message in console with details.')
logging.info('Testing info message in console with details.')
logging.warning('Testing warning message in console with details.')
logging.error('Testing error message in console with details.')
logging.critical('Testing critical message in console with details.')

print()

# Test disk logging with JSON and regular rotation
logging.debug('Starting test: Disk logging with JSON and regular rotation...')
time.sleep(2)
apv.setup_logging(level='DEBUG', log_to_disk=True, max_log_size=1024, max_backups=3, log_file_name='json_log', json_log=True, show_details=True)
for i in range(100):
    log_level = random.choice([logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL])
    logging.log(log_level, f'Log entry {i+1} for JSON & regular rotation test.')
    time.sleep(0.1)

print()

# Test disk logging with rotation & compression
logging.debug('Starting test: Disk logging with rotation & compression...')
time.sleep(2)
apv.setup_logging(level='DEBUG', log_to_disk=True, max_log_size=1024, max_backups=3, log_file_name='plain_log', show_details=True, compress_backups=True)
for i in range(100):
    log_level = random.choice([logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL])
    logging.log(log_level, f'Log entry {i+1} for disk rotation & compression test.')
    time.sleep(0.1)

logging.info('Test completed. Check the logs directory for disk logging & JSON logging tests.')

print()

try:
    import ecs_logging
except ImportError:
    pass
else:
    # Test ECS logging
    logging.debug('Starting test: ECS logging...')
    time.sleep(2)
    apv.setup_logging(level='DEBUG', ecs_log=True)
    logging.debug('This is a test log message to ECS.')
    logging.info('This is a test log message to ECS.')
    logging.warning('This is a test log message to ECS.')
    logging.error('This is a test log message to ECS.')
    logging.critical('This is a test log message to ECS.')

print()

# Test Graylog handler (Uncomment & configure to test)
# logging.debug('Starting test: Graylog handler...')
# time.sleep(2)
# apv.setup_logging(level='DEBUG', enable_graylog=True, graylog_host='your_graylog_host', graylog_port=12201)
# logging.debug('This is a test log message to Graylog.')
# logging.info('This is a test log message to Graylog.')
# logging.warning('This is a test log message to Graylog.')
# logging.error('This is a test log message to Graylog.')
# logging.critical('This is a test log message to Graylog.')

# Test CloudWatch handler (Uncomment & configure to test)
# logging.debug('Starting test: CloudWatch handler...')
# time.sleep(2)
# apv.setup_logging(level='DEBUG', enable_cloudwatch=True, cloudwatch_group_name='your_log_group', cloudwatch_stream_name='your_log_stream')
# logging.debug('This is a test log message to CloudWatch.')
# logging.info('This is a test log message to CloudWatch.')
# logging.warning('This is a test log message to CloudWatch.')
# logging.error('This is a test log message to CloudWatch.')
# logging.critical('This is a test log message to CloudWatch.')
