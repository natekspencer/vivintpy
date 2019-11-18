#!/usr/bin/env python
"""pyvivint setup script."""

from setuptools import setup, find_packages

install_requires = [
    'aiohttp>=3.6',
    'certifi>=2019.9.11'
]

setup(
    name='pyvivint',
    version='0.1.6',
    description='Python module to interact with VivintSky API.',
    long_description=open('README.md').read(),
    author='Ovidiu Stateina',
    author_email='ovidiurs@gmail.com',
    license='MIT',
    install_requires=install_requires,
    packages=find_packages(),
    url='https://github.com/ovirs/pyvivint',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Home Automation"]
)
