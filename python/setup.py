#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='knesset-data',
    version='1.3.0',
    description='API for access to available Israeli Parliament (Knesset) data',
    author='Ori Hoch',
    author_email='ori@uumpa.com',
    license='GPLv3',
    url='https://github.com/hasadna/knesset-data',
    packages=find_packages(exclude=["tests", "test.*"]),
    install_requires=['beautifulsoup4', 'pyslet', 'requests', 'simplejson', 'pyth',
                      'python-hebrew-numbers', 'cached-property', 'octohub', 'datapackage',
                      'requests', 'PySocks'],
)
