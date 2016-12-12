#!/usr/bin/env python3

from setuptools import setup

setup(
    name='botbot',
    version='0.3.0',
    description='A meta-bot for Euphoria.',
    author='Rishov Sarkar',
    url='https://github.com/ArkaneMoose/BotBot',
    license='MIT',
    packages=['botbot'],
    package_dir={'botbot': 'source'},
    install_requires=['eupy >=1.0, <2.0'],
    dependency_links=['git+https://github.com/ArkaneMoose/EuPy.git@5addd782f22068d92cedc17c3d48c47c37884522#egg=eupy-1.0'],
    entry_points={
        'console_scripts': [
            'botbot = botbot.__main__:main'
        ]
    }
)
