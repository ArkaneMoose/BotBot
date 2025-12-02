#!/usr/bin/env python3

from setuptools import setup

setup(
    name='botbot',
    version='0.5.4',
    description='A meta-bot for Euphoria.',
    author='Rishov Sarkar',
    url='https://github.com/ArkaneMoose/BotBot',
    license='MIT',
    packages=['botbot'],
    install_requires=['eupy >=1.2, <2.0', 'simpleeval >=0.9, <0.10'],
    dependency_links=['git+https://github.com/ArkaneMoose/EuPy.git@2716bc40d7514726d85f22720a3ec0fc98471a43#egg=eupy-1.2.1', 'git+https://github.com/ArkaneMoose/simpleeval.git@ac33b805645ca616f11e64bb3330a12bc5fba658#egg=simpleeval-0.9.2'],
    entry_points={
        'console_scripts': [
            'botbot = botbot.__main__:main'
        ]
    }
)
