from setuptools import setup, find_packages

setup(
    name='hierarchical_ltl_stap',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'matplotlib==3.8.1',
        'networkx==3.1',
        'numpy==1.25.2',
        'setuptools==68.0.0',
        'sympy==1.12',
    ],
    author='Xusheng Luo',
    author_email='xusheng.luo2@gmail.com',
    description='Cource code for the paper "Simultaneous Task Allocation and Planning for Multi-Robots under Hierarchical Temporal Logic Specifications"',
    license='MIT',
    url='https://github.com/XushengLuo92/Hierarchical-LTL-STAP',
)