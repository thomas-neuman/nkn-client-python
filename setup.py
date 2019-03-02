#!/usr/bin/env python

from setuptools import setup

setup(
		name='NKN Client for Python',
    version='0.1',
    description='Client for the NKN Network',
    author='Thomas Neuman',
		url='https://github.com/thomas-neuman/nkn-client-python/',
    packages=[
      'nkn_client',
      'nkn_client.jsonrpc'
    ],
		package_dir={
      'nkn_client': 'src',
    },
    install_requires=[
      'requests',
      'websockets'
    ],
    test_suite='test',
    tests_require=[
      'responses'
    ],
)
