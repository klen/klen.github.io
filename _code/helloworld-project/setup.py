from os.path import join, dirname

from setuptools import setup, find_packages

import helloworld


setup(
    name='helloworld',
    version=helloworld.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    include_package_data=True,
    install_requires=[
            'Flask==0.8'
        ],
    entry_points={
        'console_scripts': [
                'helloworld = helloworld.core:print_message',
                'serve = helloworld.web:run_server',
            ]
    },
    test_suite='tests'
)
