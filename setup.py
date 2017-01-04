#!/usr/bin/env python3

from setuptools import setup

setup(
    name='botbot',
    version='0.5.0',
    description='A meta-bot for Euphoria.',
    author='Rishov Sarkar',
    url='https://github.com/ArkaneMoose/BotBot',
    license='MIT',
    packages=['botbot'],
    package_dir={'botbot': 'source'},
    install_requires=['eupy >=1.0, <2.0', 'simpleeval >=0.9, <0.10'],
    dependency_links=['git+https://github.com/ArkaneMoose/EuPy.git@a569c35ea76a40b241a57669054b3247c3b4f960#egg=eupy-1.1', 'git+https://github.com/ArkaneMoose/simpleeval.git@ac33b805645ca616f11e64bb3330a12bc5fba658#egg=simpleeval-0.9.2'],
    entry_points={
        'console_scripts': [
            'botbot = botbot.__main__:main'
        ]
    }
)
