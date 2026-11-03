import argparse
import logging

from oscterm.logging_config import setup_logging
from oscterm.terminal import start_terminal


logger = logging.getLogger(__name__)


# TODO: send port without host sends to localhost
# TODO: listen port without host listens on 0.0.0.0

def main() -> int:
    setup_logging(
        console_level=logging.INFO
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--lhost",
        type=str,
        help="Listener hostname or IP address, used for receiving OSC messages. If a port is specified without a host, then 0.0.0.0 is used.",
        default="0.0.0.0"
    )

    parser.add_argument(
        "--lport",
        type=int,
        help="Listener port number, used for receiving OSC messages"
    )

    parser.add_argument(
        "--shost",
        type=str,
        help="The hostname or IP address of the remote machine to send OSC messages to. If a port is specified without a host, then localhost is used.",
        default="localhost"
    )

    parser.add_argument(
        "--sport",
        type=int,
        help="The port number of the remote machine to send OSC messages to"
    )

    try:
        args = parser.parse_args()

    except Exception:
        logger.exception(f"Something went wrong parsing arguments.")
        return 1

    # Start the OSC terminal
    try:
        start_terminal(
            listen_host=args.lhost,
            listen_port=args.lport,
            send_host=args.shost,
            send_port=args.sport
        )

    except Exception:
        logger.exception(f"Something went wrong starting the OSC terminal.")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
