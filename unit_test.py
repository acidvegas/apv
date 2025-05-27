#!/usr/bin/env python3
# Advanced Python Logging - Developed by acidvegas in Python (https://git.acid.vegas/apv)
# unit_test.py

import logging
import os
import random
import sys
import time

sys.dont_write_bytecode = True # FUCKOFF __pycache__

import apv


def test_console_logging():
	'''Test basic console logging functionality'''

	print('\nTesting Console Logging...')
	apv.setup_logging(level='DEBUG', date_format='%H:%M:%S')
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message in console.')
	time.sleep(1)


def test_json_console_logging():
	'''Test JSON console logging'''

	print('\nTesting JSON Console Logging...')
	apv.setup_logging(level='DEBUG', date_format='%H:%M:%S', json_log=True, log_to_disk=False)
	logging.info('Test JSON console message with custom field', extra={'_custom_field': 'test value'})
	logging.warning('Test JSON console warning with error', exc_info=Exception('Test error'))
	time.sleep(1)


def test_detailed_logging():
	'''Test console logging with details'''

	print('\nTesting Detailed Logging...')
	apv.setup_logging(level='DEBUG', show_details=True)
	for level in ['debug', 'info', 'warning', 'error', 'critical']:
		getattr(logging, level)(f'Testing {level} message with details.')
	time.sleep(1)


def test_file_logging():
	'''Test file logging with rotation'''

	print('\nTesting File Logging...')
	log_file = 'logs/test_log.log'
	apv.setup_logging(level='DEBUG', log_to_disk=True, max_log_size=1024, max_backups=3, log_file_name='test_log')
	for i in range(50):
		level = random.choice(['debug', 'info', 'warning', 'error', 'critical'])
		getattr(logging, level)(f'File logging test message {i}')
	
	assert os.path.exists(log_file), "Log file was not created"
	time.sleep(1)


def test_json_logging():
	'''Test JSON format logging'''

	print('\nTesting JSON Logging...')
	apv.setup_logging(level='DEBUG', log_to_disk=True, log_file_name='json_test', json_log=True)
	logging.info('Test JSON formatted log message')
	assert os.path.exists('logs/json_test.json'), "JSON log file was not created"
	time.sleep(1)


def test_compressed_logging():
	'''Test compressed log files'''

	print('\nTesting Compressed Logging...')
	apv.setup_logging(level='DEBUG', log_to_disk=True, max_log_size=512, max_backups=2, log_file_name='compressed_test', compress_backups=True)
	for i in range(100):
		logging.info(f'Testing compression message {i}')
	time.sleep(1)
	# Check for .gz files
	gz_files = [f for f in os.listdir('logs') if f.startswith('compressed_test') and f.endswith('.gz')]
	assert len(gz_files) > 0, 'No compressed log files were created'


if __name__ == '__main__':
	# Create logs directory if it doesn't exist
	os.makedirs('logs', exist_ok=True)
	
	# Run all tests
	test_console_logging()
	test_json_console_logging()
	test_detailed_logging()
	test_file_logging()
	test_json_logging()
	test_compressed_logging()

	print('\nAll tests completed successfully!')