#!/usr/bin/env python3
# Advanced Python Logging - Developed by acidvegas in Python (https://git.acid.vegas/apv)
# unit_test.py

import logging
import os
import random
import sys
import time

import apv


def test_console_logging():
	'''Test console logging'''

	print('\nTesting Console Logging...')
	apv.setup_logging(level='DEBUG', date_format='%H:%M:%S')
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message in console.')
	
	print('\nTesting Console Logging with Details...')
	apv.setup_logging(level='DEBUG', date_format='%H:%M:%S', show_details=True)
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message with details in console.')
		
	print('\nTesting JSON Console Logging...')
	apv.setup_logging(level='DEBUG', json_log=True)
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message with JSON format in console.')
	logging.info('Test JSON console message with custom field', extra={'_custom_field': 'test value'})
	logging.warning('Test JSON console warning with error', exc_info=Exception('Test error'))


def test_file_logging():
	'''Test file logging'''

	print('\nTesting File Logging...')
	apv.setup_logging(level='DEBUG', compress_backups=True, log_to_disk=True, max_log_size=1024, max_backups=3, log_file_name='test_log')
	for i in range(1000):
		level = random.choice(['debug', 'info', 'warning', 'error', 'critical'])
		getattr(logging, level)(f'File logging test message {i} in file.')
	assert os.path.exists('logs/test_log.log'), "Log file was not created"
	gz_files = [f for f in os.listdir('logs') if f.startswith('test_log') and f.endswith('.gz')]
	assert len(gz_files) > 0, 'No compressed log files were created'

	print('\nTesting JSON Logging...')
	apv.setup_logging(level='DEBUG', log_to_disk=True, log_file_name='json_test', json_log=True)
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message with JSON format in file.')
	assert os.path.exists('logs/json_test.json'), "JSON log file was not created"


def test_syslog_logging():
	'''Test syslog logging'''

	print('\nTesting Syslog Logging...')
	apv.setup_logging(level='DEBUG', syslog=True)
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message in syslog.')

	print('\nTesting Syslog Logging with Details...')
	apv.setup_logging(level='DEBUG', syslog=True, show_details=True)
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message with details in syslog.')


	print('\nTesting Syslog Logging with JSON Format...')
	apv.setup_logging(level='DEBUG', syslog=True, json_log=True)
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message with JSON format in syslog.')



if __name__ == '__main__':
	test_console_logging()
	test_file_logging()
	test_syslog_logging()

	print('\nAll tests completed successfully!')