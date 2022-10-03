#!/usr/bin/python3
# coding: utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='hass-desktop-sensor',
    version='1.0.1',
    description='Desktop activity sensor for Home Assistant',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="home assistant desktop sensor idle activity",
    license="MIT",
    author='ShellCode',
    author_email='shellcode33@protonmail.ch',
    url='https://github.com/ShellCode33/HASS-Desktop-Sensor',
    packages=find_packages(),
    python_requires='>=3.6',

    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX :: Linux",
    ],

    install_requires=[
        "humanize",
        "psutil",
        "requests",
    ],

    entry_points={
        "console_scripts": [
            "hass_desktop_sensor = desktop_sensor.manager:main",
        ]
    }
)
