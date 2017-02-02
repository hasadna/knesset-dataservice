#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='knesset-data-django',
    version='1.3.0',
    description='Django apps / modules for handling Israeli parliament (Knesset) data',
    author='Ori Hoch',
    author_email='ori@uumpa.com',
    license='GPLv3',
    url='https://github.com/hasadna/knesset-data',
    packages=find_packages(exclude=["tests", "test.*"]),
    install_requires=['knesset-data', 'django'],
)
