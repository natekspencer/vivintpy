#!/usr/bin/env python
"""pyvivint setup script."""

from setuptools import find_packages, setup

install_requires = ["aiohttp>=3.6", "certifi>=2019.9.11", "pubnub>=5.0.1"]

setup(
    name="pyvivint",
    version="2021.1.1",
    description="Python module to interact with VivintSky API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ovidiu Stateina, Nathan Spencer",
    author_email="ovidiurs@gmail.com",
    license="MIT",
    install_requires=install_requires,
    packages=find_packages(),
    url="https://github.com/ovirs/pyvivint",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Home Automation",
    ],
)
