#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

version = ''
with open('src/vector_prisma/__init__.py', encoding='utf-8') as f:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if not match:
        raise RuntimeError('version is not set')

    version = match.group(1)

if not version:
    raise RuntimeError('version is not set')

setup(
    name='vector-prisma',
    version=version,
    author='R-Okauchi',
    author_email='',
    maintainer='R-Okauchi',
    license='APACHE',
    url='https://github.com/R-Okauchi/vector-prisma.git',
    description='Prisma Client Python with pgvector',
    install_requires=[
        "prisma>=0.15.0",
    ],
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(
        where='src',
        include=['vector_prisma', 'vector_prisma.*'],
    ),
    package_dir={'': 'src'},
    python_requires='>=3.8.0',
    package_data={'': ['generator/templates/**/*.py.jinja', 'py.typed']},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'vector-prisma=vector_prisma.cli:main',
        ],
        'vector-prisma': [],
    },
    keywords=[
        'orm',
        'mysql',
        'typing',
        'prisma',
        'sqlite',
        'database',
        'postgresql',
        'vector',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Typing :: Typed',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
    ],
)