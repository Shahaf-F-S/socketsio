# build.py

import os
import codecs
import pathlib
from setuptools import setup as _setup, find_namespace_packages
from typing import Iterable, Any

__all__ = [
    "Dependencies",
    "parse_requirements",
    "unfold",
    "get_dependencies",
    "build_manifest",
    "build_pyproject",
    "collect_files",
    "setup"
]

class Dependencies:
    """A class to represent dependencies."""

    def __init__(
            self,
            requirements: Iterable[str] = None,
            links: Iterable[str] = None
    ) -> None:
        """
        Defines the class attributes.

        :param requirements: The requirement names and settings.
        :param links: The requirement links.
        """

        if requirements is None:
            requirements = []
        # end if

        if links is None:
            links = []
        # end if

        self.requirements = requirements
        self.links = links
    # end __init__
# end Dependencies

def parse_requirements(
        source: str | pathlib.Path,
        excluded: Iterable[str] = None
) -> Dependencies:
    """
    Parses the requirements file.

    :param source: The source of the requirements.
    :param excluded: Names of dependencies to exclude.

    :return: A dependencies object.
    """

    if excluded is None:
        excluded = []
    # end if

    links = []
    requirements = []

    with codecs.open(source, 'r') as requirements_txt:
        for line in requirements_txt.readlines():
            line = line.replace("\n", "")

            if not line or line.replace(" ", "").startswith("#"):
                continue
            # end if

            line = line[:line.find("#")] if "#" in line else line

            requirement = line.split(";")

            for i, part in enumerate(parts := requirement[0].split()):
                name = parts[0]

                for char in ['=', '<', ">"]:
                    name = name[:name.find(char)] if char in name else name
                # end for

                if name in excluded:
                    continue
                # end if

                if (
                    (len(parts) > 2) and
                    (part in ("--extra-index-url", "--index-url", "--find-links"))
                ):
                    if i == 0:
                        name = parts[-1]

                    else:
                        name = parts[0]
                    # end if

                    if name in excluded:
                        continue
                    # end if

                    links.append(f"{parts[1]}#egg={name}")
                    requirements.append(";".join([name] + requirement[1:]))

                    break
                # end if

                if len(parts) == 1 and name not in excluded:
                    requirements.append(line)
                # end if
            # end for
        # end for
    # end open

    return Dependencies(
        requirements=requirements,
        links=links
    )
# parse_requirements

def unfold(obj: Any, /, indentation: int = None) -> str:
    """
    Unfolds the object if it is an iterable.

    :param obj: The object to convert to a string.
    :param indentation: The indentation level.

    :return: The string representation of the object.
    """

    try:
        if isinstance(obj, str):
            raise TypeError
        # end if

        string = str(obj)

        if not string:
            raise TypeError
        # end if

        if indentation is None:
            indentation = 1
        # end if

        return (
                string[0] + "\n" + ("\t" * indentation) +
                (
                    (",\n" + ("\t" * indentation)).join(
                        (
                            unfold(element, indentation=indentation + 1)
                            for element in iter(obj)
                        )
                        if not isinstance(obj, dict) else
                        (
                            (
                                f"{unfold(key, indentation=indentation + 1)}: "
                                f"{unfold(value, indentation=indentation + 1)}"
                            )
                            for key, value in obj.items()
                        )
                    )
                ) + "\n" + ("\t" * (indentation - 1)) +
                string[-1]
        )

    except TypeError:
        if isinstance(obj, bool):
            return repr(obj).lower()
        # end if

        return repr(obj)
    # end try
# end unfold

def get_dependencies(
        *,
        requirements: str | pathlib.Path = None,
        dev_requirements: str | pathlib.Path = None
) -> tuple[Dependencies, Dependencies]:
    """
    Runs the program to create the package.

    :param requirements: The requirement names and settings.
    :param dev_requirements: The requirement names and settings.
    """

    if requirements is not None and os.path.exists(requirements):
        dependencies = parse_requirements(source=requirements)

        if dev_requirements is not None and os.path.exists(dev_requirements):
            extra_dependencies = parse_requirements(source=dev_requirements)

            with codecs.open(requirements, 'r') as req_file:
                reqs = req_file.read()
            # end open

            with codecs.open(dev_requirements, 'r') as req_dev_file:
                dev_reqs = req_dev_file.read()
            # end open

            if reqs not in dev_reqs:
                with codecs.open(dev_requirements, 'a') as req_dev_file:
                    req_dev_file.write(f"\n\n{reqs}")
                # end open
            # end if

        else:
            extra_dependencies = Dependencies()
        # end if

    else:
        dependencies = Dependencies()
        extra_dependencies = Dependencies()
    # end if

    return dependencies, extra_dependencies
# end get_dependencies

def build_pyproject(
        project: str | pathlib.Path = None, **kwargs: Any
) -> None:
    """
    Builds the package.

    :param project: The project configuration toml file.
    :param kwargs: Any keyword argument.
    """

    if project is not None:
        content = "\n".join(
            [
                f"{key} = {unfold(value, indentation=1)}"
                for key, value in kwargs.items() if not (
                    isinstance(value, dict) or
                    (
                        key in (
                            "long_description",
                            "license",
                            'include_package_data',
                            'dependency_links',
                            'url',
                            'install_requires',
                            'extras_require',
                            'author',
                            'packages',
                            'author_email',
                            "data_files",
                            "long_description_content_type"
                        )
                    )
                )
            ]
        )

        if os.path.exists(project):
            with codecs.open(project, 'r') as project_file:
                project_content = project_file.read()
            # end open

        else:
            project_content = ""
        # end if

        if content not in project_content:
            with codecs.open(project, 'w') as req_dev_file:
                req_dev_file.write(
                    '[build-system]\n'
                    'requires = ["setuptools"]\n'
                    'build-backend = "setuptools.build_meta"\n'
                    f'\n[project]\n{content}'
                )
            # end open
        # end if
    # end if
# end build_pyproject

def build_manifest(
        include: Iterable[str] = None, manifest: bool = None
) -> None:
    """
    Builds the manifest file.

    :param include: The files to include.
    :param manifest: The value to read the content from the file.
    """

    if not os.path.exists("MANIFEST.in") or not manifest:
        with codecs.open("MANIFEST.in", 'w') as include_file:
            include_file.write("")
        # end open
    # end if

    if os.path.exists("MANIFEST.in"):
        with codecs.open("MANIFEST.in", 'r') as include_file:
            include_content = include_file.read()
        # end open

        with codecs.open("MANIFEST.in", 'a') as include_file:
            for line in include:
                if line not in include_content:
                    include_file.write(f"include {line}\n")
                # end if
            # end for
        # end open
    # end if
# end build_manifest
def collect_files(location: str | pathlib.Path, levels: int = None) -> list[str]:
    """
    Collects all the file paths from the location with the extension.

    :param location: The location of the files.
    :param levels: The search levels.

    :return: A list of file paths.
    """

    paths = []

    if levels == 0:
        return paths
    # end if

    for name in os.listdir(location):
        path = pathlib.Path(location) / pathlib.Path(name)

        if path.is_file():
            paths.append(str(path))

        elif path.is_dir():
            paths.extend(
                collect_files(
                    str(path), levels=(
                        levels - 1 if levels is not None else levels
                    )
                )
            )
        # end if
    # end for

    return paths
# end collect_files

def setup(
        package: str | pathlib.Path, *,
        readme: str | bool | pathlib.Path = None,
        exclude: Iterable[str | pathlib.Path] = None,
        include: Iterable[str | pathlib.Path] = None,
        requirements: str | pathlib.Path = None,
        dev_requirements: str | pathlib.Path = None,
        project: str | pathlib.Path = None,
        manifest: bool = None,
        **kwargs: Any
) -> None:
    """
    Runs the program to create the package.

    :param package: The package path.
    :param readme :The path to the readme file.
    :param exclude: The paths to exclude.
    :param include: The paths to include.
    :param requirements: The requirement names and settings.
    :param dev_requirements: The requirement names and settings.
    :param project: The project configuration toml file.
    :param manifest: The value to read the content from the file.
    :param kwargs: The setup kwargs.
    """

    if include is None:
        include = []

    else:
        include = list(include)
    # end if

    if readme in (None, True):
        readme = 'README.md' if os.path.exists('README.md') else None
    # end if

    if exclude is None:
        exclude = ()
    # end if

    if isinstance(readme, (str, pathlib.Path)):
        with codecs.open(str(readme), 'r') as desc_file:
            long_description = desc_file.read()
        # end open

    else:
        long_description = None
    # end if

    dependencies, extra_dependencies = get_dependencies(
        requirements=requirements, dev_requirements=dev_requirements
    )

    include = list(
        set(
            include + [
                file for file in
                [requirements, dev_requirements, project, "build.py"]
                if file and os.path.exists(str(file))
            ]
        )
    )

    for included in list(include):
        if included is not None and os.path.isdir(str(included)):
            include += list(set(collect_files(location=included)))
        # end if
    # end for

    include = [str(pathlib.Path(path)) for path in include]

    packages = [
        f"{'.'.join(pathlib.Path(str(package)).parts)}.{content}"
        for content in find_namespace_packages(package, exclude=exclude)
    ] + [package]

    kwargs.setdefault("extras_require", {}).setdefault(
        "dev", [
            req for req in extra_dependencies.requirements
            if req not in dependencies.requirements
        ]
    )

    build_manifest(include=include, manifest=manifest)

    if project:
        build_pyproject(project=project, **kwargs)
    # end if

    _setup(
        **(dict(project=project) if project else {}),
        packages=packages,
        long_description=long_description,
        include_package_data=True,
        dependency_links=dependencies.links,
        install_requires=dependencies.requirements,
        **kwargs
    )
# end setup