from setuptools import setup

setup(
    name='botbot',
    version='0.1.1',
    description='A meta-bot for Euphoria.',
    author='Rishov Sarkar',
    url='https://github.com/ArkaneMoose/BotBot',
    license='MIT',
    packages=['botbot'],
    package_dir={'botbot': 'source'},
    install_requires=['eupy >=1.0, <2.0'],
    dependency_links=['git+https://github.com/jedevc/EuPy.git@15ce6bbd4be61b2219fec2423366ce4751bec563#egg=eupy-1.0'],
    entry_points={
        'console_scripts': [
            'botbot = botbot.__main__:main'
        ]
    }
)
