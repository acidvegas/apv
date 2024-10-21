#!/usr/bin/env python3
# Advanced Python Logging - Developed by acidvegas in Python (https://git.acid.vegas/apv)
# setup.py

from setuptools import setup, find_packages

setup(
    name='apv',
    version='1.0.0',
    description='Advanced Python Logging',
    author='acidvegas',
    url='https://git.acid.vegas/apv',
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
    ],
)