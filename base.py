# base.py

import sys
import inspect
import importlib
import subprocess
import contextlib
import warnings
import logging
import ctypes
import os
from pathlib import Path
import threading
from typing import Any, Optional, Dict

__all__ = [
    "terminate_thread",
    "suppress",
    "run_silent_command",
    "validate_requirement",
    "retrieve_name",
    "documentation",
    "document",
    "virtualenv_interpreter_location",
    "activate_virtualenv_command",
    "root",
    "source",
    "assets",
    "dependencies"
]

def root() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    try:
        if os.getcwd() in os.environ['VIRTUAL_ENV']:
            path = Path(__file__).parent

        else:
            raise KeyError
        # end if

    except KeyError:
        if os.getcwd() not in (
                path := str(Path(__file__).parent)
        ):
            path = os.getcwd()
        # end if
    # end try

    return str(path)
# end root

def source() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(root()) / Path("source"))
# end source

def assets() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(source()) / Path("assets"))
# end assets

def dependencies() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(source()) / Path("dependencies"))
# end dependencies


def terminate_thread(thread: threading.Thread) -> None:
    """
    Terminates a thread from another thread.

    :param thread: The thread instance.
    """

    logging.disable(logging.FATAL)

    thread_id = thread.ident

    if ctypes.pythonapi.PyThreadState_SetAsyncExc(
        thread_id, ctypes.py_object(SystemExit)
    ) > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
    # end if

    logging.getLogger().setLevel(logging.FATAL)
# end terminate_thread

def suppress(silence: Optional[bool] = True) -> contextlib.AbstractContextManager:
    """
    Suppresses the output.

    :param silence: The value to silence.

    :return: The output suppressor.
    """

    if not silence:
        return contextlib.nullcontext()
    # end if

    with warnings.catch_warnings(record=True):
        return contextlib.redirect_stdout(None)
    # end catch_warnings
# end suppress

def run_silent_command(command: str) -> None:
    """
    Runs a command with no output.

    :param command: The command to run.
    """

    subprocess.run(list(command.split(" ")), capture_output=True)
# end run_silent_command

def virtualenv_interpreter_location() -> str:
    """
    Returns the location of the interpreter in the venv.

    :return: The location of the interpreter.
    """

    return os.path.split(sys.executable)[0]
# end activate_virtualenv_command

def activate_virtualenv_command() -> str:
    """
    Returns the command to activate the virtual env.

    :return: The command to activate the venv.
    """

    python_startup = (
        virtualenv_interpreter_location() /
        Path('activate')
    )

    return (
        f"{'' if 'win' in sys.platform else 'source '}"
        f"{python_startup}"
    )
# end activate_virtualenv_command

def validate_requirement(
        name: str,
        path: Optional[str] = None,
        version: Optional[str] = None,
        quiet: Optional[bool] = True,
        silence: Optional[bool] = False
) -> None:
    """
    Installs the required package.

    :param name: The name of the package.
    :param path: The path to the package.
    :param version: The version to install.
    :param quiet: The value to show the installation process.
    :param silence: The value to silence.
    """

    if version is None:
        version = ""

    elif isinstance(version, str) and ("=" not in version):
        version = f"~{version}"

    else:
        version = ""
    # end if

    try:
        importlib.import_module(name)

    except ImportError:
        arguments = [
            'install',
            f'{(path if path is not None else name) + version}'
        ]

        if quiet:
            arguments.append("--quiet")
        # end if

        command = (
            f"{activate_virtualenv_command()} && "
            f"{Path(virtualenv_interpreter_location()) / Path('python')} -m pip "
            f"{' '.join(arguments)}"
        )

        if silence:
            with suppress():
                os.system(command)
            # end suppress

        else:
            os.system(command)
        # end if

        try:
            importlib.import_module(name)

        except ImportError:
            raise ImportError(f"{name} module is not found.")
        # end try
    # end try
# end validate_requirements

def retrieve_name(variable: Any, level: Optional[int] = 1) -> str:
    """
    Gets the name of the source variable of the parameter.

    :param variable: The variable to get its source name.
    :param level: The level of outer frame to search for.

    :return: The source name of the variable.
    """

    src = inspect.currentframe()

    for _ in range(level):
        src = src.f_back
    # end for

    return [
        var_name for var_name, var_val in
        src.f_locals.items()
        if var_val is variable
    ][0]
# end retrieve_name

def documentation(module: str) -> Dict[str, str]:
    """
    Documents a module with its content objects documentation.

    :param module: The name of the module.

    :return: The documentation of the module.
    """

    documents = {
        f"{value.__module__}.{value.__name__}": value
        for name, value in sorted(
            list(sys.modules[module].__dict__.items()),
            key=lambda item: item[0]
        )
        if (
            hasattr(value, '__module__') and
            hasattr(value, '__name__') and
            hasattr(value, '__doc__') and
            hasattr(value, '__init__')
        )
    }

    return {
        key: f'`{key}`\n{value.__doc__}'
        for key, value in documents.items()
    }
# end documentation

def document(obj: Any) -> None:
    """
    Documents a module with its content objects documentation.

    :param obj: The obj to document.
    """

    obj.__doc__ += """\n\n""".join(
        documentation(obj.__module__).values()
    )
# end document