#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="k8sdrutils",
    version="0.0.4",
    author="WW",
    description="Utils related to backup & restore",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paulcarlton-ww/k8s-dr-utils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['boto3', 
                      'kubernetes'],
    extras_require={
        'dev': ['pytest',
                'pytest-cov',
                'pytest-mock',
                'pylint'],
    },
    packages=setuptools.find_packages()
)