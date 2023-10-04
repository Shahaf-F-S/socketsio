# communication.py

import warnings
from typing import (
    Optional, Any, Callable, Type, Iterable
)
from contextlib import contextmanager

__all__ = [
    "handler"
]

@contextmanager
def handler(
        success_callback: Optional[Callable[[], Any]] = None,
        exception_callback: Optional[Callable[[], None]] = None,
        cleanup_callback: Optional[Callable[[], Any]] = None,
        exception_handler: Optional[Callable[[Exception], Any]] = None,
        exceptions: Optional[Iterable[Type[Exception]]] = None,
        warn: Optional[bool] = True,
        catch: Optional[bool] = False,
        silence: Optional[bool] = True
) -> Any:
    """
    Handles the communication between the server and client.

    :param success_callback: The callback to run for success.
    :param exception_handler: The exception handler.
    :param exception_callback: The callback to run for exception.
    :param cleanup_callback: The callback to run on finish.
    :param exceptions: The exceptions to catch.
    :param catch: The value to not raise an exception.
    :param silence: The value to silence the output.
    :param warn: The value to raise a warning instead of printing the message.

    :return: Any returned value.
    """

    try:
        if success_callback is None:
            yield

        else:
            yield success_callback()
        # end if

    except (
        exceptions or
        (
            ConnectionError,
            ConnectionRefusedError,
            ConnectionAbortedError,
            ConnectionResetError
        )
    ) as e:
        if exception_callback is not None:
            exception_callback()
        # end if

        if exception_handler is None:
            if catch:
                if not silence:
                    message = f"{type(e).__name__}: {str(e)}"

                    if warn:
                        warnings.warn(message)

                    else:
                        print(message)
                    # end if
                # end if

            else:
                raise e
            # end if

        else:
            exception_handler(e)
        # end if

    finally:
        if cleanup_callback is not None:
            cleanup_callback()
        # end if
    # end try
# end handler