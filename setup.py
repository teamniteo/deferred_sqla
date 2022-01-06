"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


version = '0.0'

setup(
    name='deferred_sqla',
    version=version,
    description='Deferred SQLAlchemy configuration library',
    long_description=long_description,
    license='Apache2',
    long_description_content_type='text/markdown',
    url='https://github.com/teamniteo/pyramid_deferred_sqla',
    author='Niteo',
    author_email='info@niteo.co',
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='sqlalchemy',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={
        '': ['LICENSE'],
    },
    install_requires=[
        'sqlalchemy',
        'alembic',
        'venusian',
        'dotted_name_resolver',
        'zope.sqlalchemy',
    ],
    setup_requires=["pytest-runner"],
    extras_require={
        'dev': ['coverage', 'pytest', 'tox'],
        'lint': ['black'],
    }
)
