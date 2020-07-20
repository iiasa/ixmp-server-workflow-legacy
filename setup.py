from setuptools import setup

setup(
    name='ixmp_workflow_utils',
    version='0.0.1',
    url='https://github.com/iiasa/ixmp_server_integration.git',
    author='Kushin Nikolay',
    author_email='kushin@iiasa.ac.at',
    description='Common utilities to use in application workflow scripts',
    packages=['ixmp_workflow_utils'],
    install_requires=[
        'pandas'
    ],
)
