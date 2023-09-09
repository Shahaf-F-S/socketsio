# document.py

import os
from pathlib import Path
from typing import Optional

from base import validate_requirement

def generate_html(
        package: str,
        destination: Optional[str] = None,
        reload: Optional[bool] = False,
        show: Optional[bool] = False
) -> None:
    """
    Generates the documentation for the package.

    :param reload: The value to rewrite the documentation.
    :param show: The value to show the documentation.
    :param package: The package to document.
    :param destination: The documentation destination.
    """

    validate_requirement("pdoc", path="pdoc3")

    from pdoc.cli import main as document, parser

    if destination is None:
        destination = "docs"
    # end if

    main_index_file = Path(destination) / Path(package) / Path("index.html")

    if reload or not main_index_file.is_dir():
        document(
            parser.parse_args(
                [
                    "--html", "--force", "--output-dir",
                    str(destination), str(package)
                ]
            )
        )
    # end if

    if show:
        os.system(f'start {main_index_file}')
    # end if
# end generate_html