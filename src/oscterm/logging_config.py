import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from oscterm.constants import app_data_folder_path

logs_folder_path = app_data_folder_path / "logs"


def setup_logging(
    log_file: Path | None = None,
    *,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> None:
    # Use the default logs location if a custom path
    # has not been specified.
    if log_file is None:
        log_file = logs_folder_path / "log.txt"

    # Make sure the destination folder exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(console_level)
    console.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=min(console_level, file_level),
        handlers=[console, file_handler],
        force=True,
    )
