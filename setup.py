#!/usr/bin/env python3
# Advanced Python Logging - Developed by acidvegas in Python (https://git.acid.vegas/apv)
# setup.py

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setup(
    name='apv',
    version='1.0.3',
    description='Advanced Python Logging',
    author='acidvegas',
    author_email='acid.vegas@acid.vegas',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/acidvegas/apv',
    project_urls={
        'Bug Tracker': 'https://github.com/acidvegas/apv/issues',
        'Documentation': 'https://github.com/acidvegas/apv/wiki',
        'Source Code': 'https://github.com/acidvegas/apv',
    },
    packages=find_packages(),
    install_requires=[
        # No required dependencies for basic functionality
    ],
    extras_require={
        'cloudwatch': ['boto3'],
        'ecs' : ['ecs-logging'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
    ],
)
