#!/usr/bin/env python3

from distutils.core import setup
import os

setup_path = os.path.abspath(os.path.dirname(__file__))


def read_description(filename):
    with open(os.path.join(setup_path, filename), 'r') as description_file:
        return description_file.read()


setup(
    name="modelsetup",
    version='0.1.0.dev1',
    author="Przemyslaw (Mack) Nowak",
    author_email="pnowak.mack@gmail.com",
    description="Utility supporting initial model setup",
    long_description=read_description("README.md"),
    url="https://github.com/macknowak/modelsetup",
    license="MIT License",
    packages=['modelsetup'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering'
        ]
    )
