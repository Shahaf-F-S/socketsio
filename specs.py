# specs.py

import io
import os
import tokenize
from typing import List, Optional, Iterable, Dict, Any
from pathlib import Path
import json

__all__ = [
    "read_file",
    "strip_code",
    "strip_code_file",
    "FilesCollection",
    "CodeFileSpecs",
    "ContentFileSpecs",
    "ProjectTree",
    "ProjectInspection",
    "ProjectSpecs",
    "inspect_project",
    "project_tree",
    "project_specs"
]

def read_file(path: str) -> str:
    """
    Reads the content inside the file.

    :param path: The file path.

    :return: The content of the file
    """

    with open(path, "r", encoding="utf-8") as file:
        return file.read()
    # end open
# end read_file

def strip_code(source: str) -> str:
    """
    Strips the code string from any docstring, comments and blank lines.

    :param source: The source code.

    :return: The stripped code.
    """

    out = ""

    last_lineno = -1
    last_col = 0

    previous_token_type = tokenize.INDENT

    io_obj = io.StringIO(source)

    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]

        if start_line > last_lineno:
            last_col = 0
        # end if

        if start_col > last_col:
            out += (" " * (start_col - last_col))
        # end if

        if token_type == tokenize.COMMENT:
            pass

        elif token_type == tokenize.STRING:
            if (
                (previous_token_type != tokenize.INDENT) and
                (previous_token_type != tokenize.NEWLINE) and
                (start_col > 0)
            ):
                out += token_string
            # end if

        else:
            out += token_string
        # end if

        previous_token_type = token_type
        last_col = end_col
        last_lineno = end_line
    # end for

    return '\n'.join(
        line for line in out.splitlines() if line.strip()
    )
# end strip_code

def strip_code_file(path: str) -> str:
    """
    Strips the code string from any docstring, comments and blank lines.

    :param path: The file path.

    :return: The stripped code.
    """

    return strip_code(read_file(path))
# end strip_code_file

FilesCollection = Dict[str, List[str]]

def collect_files(
        location: str, extensions: Optional[Iterable[str]] = None,
        excluded_names: Optional[Iterable[str]] = None,
        levels: Optional[int] = None
) -> FilesCollection:
    """
    Collects all the file paths from the location with the extension.

    :param location: The location of the files.
    :param extensions: The file extensions.
    :param levels: The search levels.
    :param excluded_names: The excluded file and directory names.

    :return: A list of file paths.
    """

    if excluded_names is None:
        excluded_names = ()
    # end if

    base_extensions = (".",)

    if extensions is None:
        extensions = base_extensions
    # end if

    paths = {extension: [] for extension in extensions}

    if levels == 0:
        return paths
    # end if

    if not any(
        part in excluded_names
        for part in Path(location).parts
    ):
        for name in os.listdir(location):
            path = Path(location) / Path(name)

            if path.is_file():
                for extension in extensions:
                    if (
                        (
                            (extensions != base_extensions) and
                            (str(path).endswith(extension))
                        ) or (extensions == base_extensions)
                    ):
                        paths[extension].append(str(path))
                    # end if
                # end for

            else:
                new_paths = collect_files(
                    str(path), extensions=extensions,
                    levels=(levels - 1 if levels is not None else levels)
                )

                for extension in paths:
                    paths[extension].extend(new_paths[extension])
                # end for
            # end if
        # end for
    # end if

    return paths
# end collect_files

class ContentFileSpecs:
    """A class for file specs."""

    def __init__(self, path: str, extension: str) -> None:
        """
        Defines the class attributes.

        :param path: The file path.
        :param extension: The file extension.
        """

        self.path = path
        self.extension = extension

        self.content = None

        self.lines_count = None
        self.words_count = None
        self.characters_count = None
    # end __init__

    def process(self) -> None:
        """Processes the file data."""

        self.content = read_file(self.path)

        self.lines_count = len(self.content.split("\n"))
        self.words_count = len(self.content.replace("\n", "").split())
        self.characters_count = len(self.content.replace(" ", ""))
    # end process
# end ContentFileSpecs

class CodeFileSpecs:
    """A class for file specs."""

    def __init__(self, path: str, extension: str) -> None:
        """
        Defines the class attributes.

        :param path: The file path.
        :param extension: The file extension.
        """

        self.path = path
        self.extension = extension

        self.content = None
        self.code = None

        self.code_lines_count = None
        self.content_lines_count = None
        self.comment_lines_count = None
        self.words_count = None
        self.characters_count = None
    # end __init__

    def process(self) -> None:
        """Processes the file data."""

        self.content = read_file(self.path)
        self.code = strip_code(self.content)

        self.code_lines_count = len(self.code.split("\n"))
        self.content_lines_count = len(self.content.split("\n"))
        self.comment_lines_count = self.content_lines_count - self.code_lines_count
        self.words_count = len(self.code.replace("\n", "").split())
        self.characters_count = len(self.code.replace(" ", ""))
    # end process
# end CodeFileSpecs

class ProjectSpecs:
    """A class for project specs."""

    def __init__(
            self, content_files_collection: FilesCollection,
            code_files_collection: FilesCollection, location: str
    ) -> None:
        """
        Defines the class attributes.

        :param location: The project location.
        :param content_files_collection: The collection of file paths.
        :param code_files_collection: The collection of file paths.
        """

        self.location = location

        self.content_files_collection = content_files_collection
        self.code_files_collection = code_files_collection

        self.content_files_count = sum(
            len(value) for value in self.content_files_collection.values()
        )
        self.code_files_count = sum(
            len(value) for value in self.code_files_collection.values()
        )

        self.content_file_extensions = list(self.content_files_collection.keys())
        self.code_file_extensions = list(self.code_files_collection.keys())
    # end __init__
# end ProjectSpecs

class ProjectTree:
    """A class to represent the project tree."""

    def __init__(self, tree: Dict[str, Any]) -> None:
        """
        Defines the class attributes.

        :param tree: The project tree.
        """

        self.tree = tree
    # end __init__
# end ProjectTree

def set_project_leaf(
        tree: Dict[str, Any], branches: List[str], leaf: Dict[str, Any]
) -> None:
    """
    Set a terminal element to a leaf within nested dictionaries.

    :param tree: The project tree object.
    :param branches: The project tree branches.
    :param leaf: The leaf to add to the tree.
    """

    if len(branches) == 1:
        tree[branches[0]] = leaf

        return
    # end if

    if branches[0] not in tree:
        tree[branches[0]] = {}
    # end if

    set_project_leaf(
        tree=tree[branches[0]], branches=branches[1:],
        leaf=leaf
    )
# end set_leaf

def project_tree(
        location: str, excluded_extensions: Optional[Iterable[str]] = None,
        excluded_names: Optional[Iterable[str]] = None
) -> ProjectTree:
    """
    Gets the project file structure tree.

    :param location: The project location.
    :param excluded_extensions: The excluded file types.
    :param excluded_names: The excluded file and directory names.

    :return: The project tree.
    """

    tree = {}

    for root, dirs, files in os.walk(location):
        branches = [location]

        if (
            (root != location) and
            (not any(part in excluded_names for part in Path(root).parts))
        ):
            branches.extend(
                Path(os.path.relpath(root, location)).parts
            )
        # end if

        files_data = []

        for file in files:
            valid = True

            for extension in excluded_extensions:
                if valid and (
                    file.endswith(extension) or
                    any(part in excluded_extensions for part in Path(file).parts)
                ):
                    valid = False
                # end if
            # end for

            if valid:
                files_data.append((file, None))
            # end if
        # end for

        directories_data = [
            (d, {}) for d in dirs
            if any(part in excluded_names for part in Path(d).parts)
        ]

        # noinspection PyTypeChecker
        set_project_leaf(
            tree=tree, branches=branches, leaf=dict(
                directories_data + files_data
            )
        )
    # end for

    return ProjectTree(tree)
# end project_tree

class ProjectInspection:
    """A class for project inspection."""

    def __init__(self, specs: ProjectSpecs, tree: ProjectTree) -> None:
        """
        Defines the class attributes.

        :param specs: The project specs object
        :param tree: The tree of the project.
        """

        self.specs = specs
        self.tree = tree

        self.location = self.specs.location

        self.content_files_collection = {}
        self.code_lines_counters = {}
        self.comment_lines_counters = {}
        self.content_lines_counters = {}
        self.code_files_collection = {}

        self.content_file_extensions = self.specs.content_file_extensions
        self.code_file_extensions = self.specs.code_file_extensions
        self.content_files_count = self.specs.content_files_count
        self.code_files_count = self.specs.code_files_count

        self.total_code_lines_count = None
        self.total_comment_lines_count = None
        self.total_content_lines_count = None
        self.total_lines_count = None
    # end __init__

    def process(self) -> None:
        """Processes the project."""

        for extension, paths in self.specs.content_files_collection.items():
            self.content_files_collection[extension] = {}
            self.content_lines_counters[extension] = 0

            for path in paths:
                content_file_specs = ContentFileSpecs(
                    path=path, extension=extension
                )
                content_file_specs.process()
                (
                    self.content_files_collection[extension][path]
                ) = content_file_specs

                self.content_lines_counters[extension] += content_file_specs.lines_count
            # end for
        # end for

        for extension, paths in self.specs.code_files_collection.items():
            self.code_files_collection[extension] = {}
            self.code_lines_counters[extension] = 0
            self.comment_lines_counters[extension] = 0

            for path in paths:
                code_file_specs = CodeFileSpecs(
                    path=path, extension=extension
                )
                code_file_specs.process()
                (
                    self.code_files_collection[extension][path]
                ) = code_file_specs

                self.code_lines_counters[extension] += code_file_specs.code_lines_count
                self.comment_lines_counters[extension] += code_file_specs.comment_lines_count
            # end for
        # end for

        self.content_file_extensions = self.specs.content_file_extensions
        self.code_file_extensions = self.specs.code_file_extensions

        self.total_code_lines_count = sum(self.code_lines_counters.values())
        self.total_comment_lines_count = sum(self.comment_lines_counters.values())
        self.total_content_lines_count = sum(self.content_lines_counters.values())
        self.total_lines_count = (
            self.total_code_lines_count +
            self.total_comment_lines_count +
            self.total_content_lines_count
        )
    # end process
# end ProjectInspection

def inspect_project(
        location: str, content_file_extensions: Optional[Iterable[str]] = None,
        code_file_extensions: Optional[Iterable[str]] = None,
        excluded_extensions: Optional[Iterable[str]] = None,
        excluded_names: Optional[Iterable[str]] = None
) -> ProjectInspection:
    """
    Defines the class attributes.

    :param location: The project location.
    :param content_file_extensions: The extensions of file paths.
    :param code_file_extensions: The extensions of file paths.
    :param excluded_extensions: The excluded file types.
    :param excluded_names: The excluded file and directory names.

    :returns: The inspection object.
    """

    return ProjectInspection(
        ProjectSpecs(
            content_files_collection=collect_files(
                location=location, extensions=content_file_extensions,
                excluded_names=excluded_names
            ),
            code_files_collection=collect_files(
                location=location, extensions=code_file_extensions,
                excluded_names=excluded_names
            ),
            location=location
        ),
        tree=project_tree(
            location=location, excluded_extensions=excluded_extensions,
            excluded_names=excluded_names,
        )
    )
# end inspect_project

class ModelEncoder(json.JSONEncoder):
    """A class to represent a json encoder."""

    excluded: Iterable[str] = []

    def default(self, obj: Any) -> Dict[str, Any]:
        """
        Returns the data to encode to json format.

        :param obj: The object to encode.

        :return: The internal data state of the object.
        """

        data = obj.__dict__.copy()

        for key in data.copy():
            if key in self.excluded:
                data.pop(key)
            # end
        # end for

        return data
    # end default
# end ModelEncoder

def project_specs(
        location: str, save: Optional[bool] = True,
        excluded_extensions: Optional[Iterable[str]] = None,
        excluded_names: Optional[Iterable[str]] = None,
        content_file_extensions: Optional[Iterable[str]] = None,
        code_file_extensions: Optional[Iterable[str]] = None
) -> ProjectInspection:
    """
    Gets the project file structure tree.

    :param location: The project location.
    :param save: The value to save the objects.
    :param excluded_extensions: The excluded file types.
    :param excluded_names: The excluded file and directory names.
    :param content_file_extensions: The extensions of file paths.
    :param code_file_extensions: The extensions of file paths.

    :return: The project specs object.
    """

    if isinstance(save, bool):
        save = "specs"
    # end if

    specs_path = Path(save) / Path(location).parts[-1]

    if not specs_path.exists():
        os.makedirs(str(specs_path), exist_ok=True)
    # end if

    inspection = inspect_project(
        location=location,
        code_file_extensions=code_file_extensions,
        content_file_extensions=content_file_extensions,
        excluded_extensions=excluded_extensions,
        excluded_names=excluded_names
    )
    inspection.process()

    ModelEncoder.excluded = excluded_names

    if save:
        with open(str(specs_path / Path("inspection.json")), "w") as file:
            json.dump(inspection, file, cls=ModelEncoder, indent=4)
        # end open
    # end if

    return inspection
# end project_specs