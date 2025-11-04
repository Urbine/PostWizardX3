"""
Workflows Logging module

This module is responsible for logging information to the console and application logs
as well as standardize styles for the console output.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
from enum import Enum
from typing import Tuple, Union, Optional, NoReturn

# Third-party imports
import pyclip
from rich.console import Console


class ConsoleStyle(Enum):
    """
    Store constants for color styles used with console objects from the ``Rich`` library.
    """

    TEXT_STYLE_ATTENTION = "bold yellow"
    TEXT_STYLE_DEFAULT = "green"
    TEXT_STYLE_ACTION = "bold green"
    TEXT_STYLE_PROMPT = "bold cyan"
    TEXT_STYLE_SPECIAL_PROMPT = "bold magenta"
    TEXT_STYLE_WARN = "bold red"


def terminate_loop_logging(
    console_obj: Console,
    iter_num: int,
    total_elems: int,
    done_count: int,
    time_elapsed: Tuple[Union[int, float], Union[int, float], Union[int, float]],
    exhausted: bool,
    sets: bool = False,
    interactive=True,
) -> NoReturn:
    """Terminate the sequence of the loop by logging messages to the screen and the logs.

    :param time_elapsed: ``tuple[int, int, int]`` | Time measurement variables that report elapsed execution time for logging.
    :param console_obj: ``rich.console.Console``  | Console object used in order to log information to the console.
    :param iter_num: ``int``    | Iteration number in main loop for logging purposes
    :param total_elems: ``int`` | Total elements that the main loop had to process
    :param done_count: ``int``  | Total of video elements that were pushed to the WordPress site.
    :param exhausted: ``bool``  | Flag that controls console logging depending on whether elements are exhausted.
    :param sets: ``bool``       | Flag that controls console logging depending on whether elements are sets.
    :param interactive: ``bool`` | Flag that controls console logging depending on whether the flow is interactive.
    :return: ``None``
    """
    # The terminating parts add this function to avoid
    # tracebacks from pyclip and enable cross-platform support.
    pyclip.detect_clipboard()
    pyclip.clear()
    if exhausted:
        logging.info(
            f"List exhausted or required post quantity reached. State: num={iter_num} total_elems={total_elems}"
        )
        if interactive:
            console_obj.print(
                "\nWe have reviewed all posts for this query.",
                style=ConsoleStyle.TEXT_STYLE_WARN.value,
            )
            console_obj.print(
                "Try a different SQL query or partner. I am ready when you are. ",
                style=ConsoleStyle.TEXT_STYLE_WARN.value,
            )
    elif not sets:
        logging.info(f"List exhausted. State: num={iter_num} total_elems={total_elems}")
        if interactive:
            console_obj.print(
                f"You have created {done_count} posts in this session!",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )
    else:
        if interactive:
            console_obj.print(
                f"You have created {done_count} sets in this session!",
                style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            )
    h, mins, secs = time_elapsed
    logging.info(
        f"User created {done_count} {'posts' if not sets else 'sets'} in hours: {h} mins: {mins} secs: {secs}"
    )
    logging.info("Cleaning system clipboard and temporary directories. Quitting...")
    logging.shutdown()
    raise KeyboardInterrupt


def iter_session_print(
    console_obj: Console,
    video_count: int,
    elem_num: int = 0,
    partner: Optional[str] = None,
) -> None:
    """Print session information and element statistics to the console using Rich library styling.

    When partner is provided, prints the total count of videos to be published for that partner.
    Otherwise, prints the current element number and count in an iteration session. Uses environment
    variables set in logging_setup() to display session ID.

    :param console_obj: ``rich.console.Console`` Console object used for styled printing
    :param video_count: ``int`` Total count of videos or current count in session
    :param elem_num: ``int`` Current element number being processed, defaults to 0
    :param partner: ``Optional[str]`` Partner name to display with video count, defaults to None
    :return: ``None``
    """

    console_obj.print(
        f"Session ID: {os.environ.get('SESSION_ID')}",
        style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
        justify="left",
    )
    if partner:
        console_obj.print(
            f"\nThere are {video_count} {partner} elements to be published...",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="center",
        )
    else:
        console_obj.print(
            f"Element #{elem_num}",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="left",
        )
        console_obj.print(
            f"Count: {video_count}",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="left",
        )
        console_obj.print(
            f"\n{' Review this element ':*^30}\n",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="center",
        )
