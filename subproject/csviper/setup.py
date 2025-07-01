"""
Setup configuration for CSViper
"""

from setuptools import setup, find_packages

with open("ReadMe.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="csviper",
    version="0.1.0",
    author="CSViper Team",
    author_email="",
    description="A CLI tool for analyzing CSV files and generating SQL import scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ftrotter/csviper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
        "mysql": [
            "pymysql>=1.0.0",
            "sqlalchemy>=1.4.0",
        ],
        "postgresql": [
            "psycopg2-binary>=2.8.0",
            "sqlalchemy>=1.4.0",
        ],
        "full": [
            "pymysql>=1.0.0",
            "psycopg2-binary>=2.8.0",
            "sqlalchemy>=1.4.0",
            "python-dotenv>=0.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "csviper=csviper.__main__:cli",
        ],
    },
)
