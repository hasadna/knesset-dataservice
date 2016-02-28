#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='knesset-data',
    version='0.0.10',
    description='API for access to available Israely Parliament (Knesset) data',
    author='Ori Hoch',
    author_email='ori@uumpa.com',
    license='GPLv3',
    url='https://github.com/hasadna/knesset-data',
    packages=find_packages(exclude=["tests", "test.*"]),
    install_requires=['beautifulsoup4', 'pyslet', 'requests', 'simplejson', 'pyth',
                      'python-hebrew-numbers', 'cached-property']
)
