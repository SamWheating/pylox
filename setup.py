
from setuptools import setup, find_packages

setup(
    name='pylox',
    version='0.0.1',
    url='https://github.com/samwheating/pylox.git',
    author='Sam Wheating',
    author_email='SamWheating@gmail.com',
    description='Python 3.10+ Implementation of the Lox programming language',
    packages=find_packages(),    
    install_requires=[],
    entry_points = {
        'console_scripts': ['pylox=pylox.pylox:main'],
    }
)