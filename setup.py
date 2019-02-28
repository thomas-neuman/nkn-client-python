#!/usr/bin/env python

from distutils.core import setup

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
      'nkn_client.jsonrpc': 'src/json-rpc',
    },
)
