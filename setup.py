from setuptools import setup

setup(
    name='botbot',
    version='0.1.0',
    description='A meta-bot for Euphoria.',
    author='Rishov Sarkar',
    url='https://github.com/ArkaneMoose/BotBot',
    license='MIT',
    packages=['botbot'],
    package_dir={'botbot': 'source'},
    install_requires=['eupy'],
    dependency_links=['https://github.com/jedevc/EuPy.git#egg=eupy']
)
