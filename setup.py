"""Package entrypoint."""
from setuptools import setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="txdps",
    version="0.0.1",
    long_description=__doc__,
    packages=["txdps"],
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
    scripts=["bin/txdps"],
    entry_points={"console_scripts": ["txdps=txdps.cli:main"]},
)
