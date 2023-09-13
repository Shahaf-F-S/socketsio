# setup.py

import codecs

with codecs.open('build.py', 'r') as build_file:
    build_source = build_file.read()

source = dict()

exec(build_source, source)

setup = source['setup']

def main() -> None:
    """Runs the function to distribute the package."""

    setup(
        package="socketsio",
        project="pyproject.toml",
        exclude=[
            "__pycache__",
            "*.pyc"
        ],
        requirements="requirements.txt",
        dev_requirements="requirements-dev.txt",
        name='pysocketsio',
        version='1.0.0',
        description=(
            "This module provides a wrapper for the built-in "
            "socket module in python. The program provides server and. "
            "client classes, with the communication methods."
        ),
        license='MIT',
        author="Shahaf Frank-Shapir",
        author_email='shahaffrs@gmail.com',
        long_description_content_type='text/markdown',
        url='https://github.com/Shahaf-F-S/socketsio',
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Operating System :: OS Independent"
        ]
    )
# end main

if __name__ == "__main__":
    main()
# end if