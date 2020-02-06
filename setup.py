import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="k8s-dr-utils",
    version="0.0.01",
    author="WW",
    description="Utils related to backup & restore",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paulcarlton-ww/k8s-dr-utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)