from setuptools import find_packages, setup
from graph_coloring_utils import __version__


setup(
    name='graph_coloring_utils',
    version=__version__,
    description='Collection of utilities to help with graph coloring problems',
    author='Didericis',
    author_email='eric@dideric.is',
    python_requires='>3.4',
    classifier=[
        'Intended Audience :: Mathematicians',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        'docopt>=0.6.2,<0.7'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gcutils=graph_coloring_utils.cli:main',
        ]
    },
)
