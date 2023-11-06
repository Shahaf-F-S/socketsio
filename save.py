# save.py

import os

from base import run_silent_command, suppress
from specs import project_specs
from document import generate_html

def main(project: str, silence: bool = True) -> None:
    """
    Runs the function to save thew project.

    :param project: The project name.
    :param silence: The value to silence the process.
    """

    commands = [
        lambda: (
            (os.system if not silence else run_silent_command)(
                "python setup.py sdist"
            )
        ),
        lambda: project_specs(
            location=project, excluded_names=["__pycache__"],
            excluded_extensions=[".pyc"], code_file_extensions=[".py"],
            content_file_extensions=[], save=True
        ),
        lambda: generate_html(package=project)
    ]

    for command in commands:
        with suppress(silence=silence):
            command()
        # end suppress
    # end for
# end main

if __name__ == "__main__":
    main(project="socketsio")
# end if