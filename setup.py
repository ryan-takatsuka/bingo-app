#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements from requirements.txt
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="bingo-card-generator",
    version="1.0.0",
    author="Bingo App Developer",
    description="A customizable bingo card generator that creates interactive HTML bingo cards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["create_bingo_card", "themes"],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "create-bingo-card=create_bingo_card:main",
            "create-spooky-bingo=create_bingo_card:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    include_package_data=True,
    package_data={
        "": ["*.jinja", "*.csv", "images/*"],
    },
)