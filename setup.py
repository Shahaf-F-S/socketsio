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
        exclude=[
            "__pycache__",
            "*.pyc"
        ],
        requirements="requirements.txt",
        name='pysocketsio',
        version='2.3.1',
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
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Operating System :: OS Independent"
        ]
    )

if __name__ == "__main__":
    main()
