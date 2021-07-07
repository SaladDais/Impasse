#!/usr/bin/env python

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='impasse',
    # Version chosen for parity with Assimp since we need ABI compatibility
    version='5.0.3',
    license='BSD',
    description='Alternate Python bindings for the Open Asset Import Library (ASSIMP)',
    long_description=readme(),
    long_description_content_type="text/markdown",
    url='https://github.com/SaladDais/Impasse',
    author='Salad Dais',
    author_email='SaladDais@users.noreply.github.com',
    packages=['impasse'],
    data_files=[
        ('share/impasse', ['README.md']),
        # TODO: Make these proper console scripts
        # ('share/examples/impasse', ['scripts/' + f for f in os.listdir('scripts/')]),
    ],
    install_requires=['numpy', 'cffi'],
    python_requires='>=3.7',
    zip_safe=False,
    tests_require=[
        "pytest",
    ],
    test_suite='tests',
)
