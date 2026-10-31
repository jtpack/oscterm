from pythonosc import dispatcher, osc_server, udp_client
import logging
import threading
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import shlex


logger = logging.getLogger(__name__)

def start_terminal(
        listen_host: str | None = None,
        listen_port: int | None = None,
        send_host: str | None = None,
        send_port: int | None = None
) -> None:
    """
    Start the interactive OSC terminal.
    If no listen host and port are supplied, then we only send OSC messages.
    If no send host and port are supplied, then we only receive OSC messages.
    :param listen_host: str or None. Can be an IP address like 192.168.5.7 or a hostname like mixer.local or localhost
    :param listen_port: int or None
    :param send_host: str or None. Can be an IP address like 192.168.5.7 or a hostname like mixer.local
    :param send_port: int or None
    :return:
    """
    #
    # Server, used for receiving OSC messages
    #

    disp = dispatcher.Dispatcher()
    disp.set_default_handler(print_osc_message)
    server = None
    thread = None

    # Start server if listen host and port have been supplied
    if listen_host is not None and listen_port is not None:
        server, thread = start_osc_server(
            host=listen_host,
            port=listen_port,
            disp=disp
        )

    #
    # Client, used for sending OSC messages
    #
    client = None

    # Create the client if a host and port have been supplied
    if send_host is not None and send_port is not None:
        client = create_osc_client(send_host, send_port)

    #
    # Prepare the interactive terminal
    #
    session = PromptSession()

    try:
        with patch_stdout():
            while True:
                try:
                    command = session.prompt("osc-term>").strip()

                    if command[0] == '/':
                        # This is a command to send an OSC message.
                        address, arguments = parse_osc_command(command)

                        if address:
                            if client is not None:
                                client.send_message(address, arguments)
                            else:
                                print("Warning: OSC send destination not set")

                    else:
                        try:
                            parts = shlex.split(command)
                            if parts[0] == 'exit':
                                break

                            elif parts[0] == 'set-listener':
                                listen_host = parts[1]

                                try:
                                    listen_port = int(parts[2])

                                    # Shut down OSC server if one already exists
                                    if server is not None and thread is not None:
                                        stop_osc_server(server, thread)

                                    # Set up OSC server to start listening for messages
                                    server, thread = start_osc_server(listen_host, listen_port, disp)

                                except ValueError:
                                    print(f"Invalid port: {parts[2]}")

                            elif parts[0] == 'set-sender':
                                send_host = parts[1]

                                try:
                                    send_port = int(parts[2])

                                    # Set up a client for sending OSC messages
                                    create_osc_client(
                                        host=send_host,
                                        port=send_port
                                    )

                                except ValueError:
                                    print(f"Invalid port: {parts[2]}")

                            elif parts[0] == 'listener':
                                if server is not None and thread is not None:
                                    print(f"Listening on {listen_host} {listen_port}")
                                else:
                                    print(f"Not listening for OSC messages")

                            elif parts[0] == 'sender':
                                if client is not None:
                                    print(f"Sending to {send_host} {send_port}")
                                else:
                                    print(f"OSC send destination not set")

                            else:
                                print(f"Unknown command: {parts[0]}")

                        except ValueError as e:
                            print(f"Parse error: {e}")

                except KeyboardInterrupt:
                    continue

    except EOFError:
        pass

    finally:
        if server is not None and thread is not None:
            stop_osc_server(server, thread)


def print_osc_message(address, *args):
    if len(args) == 0:
        print(f"{address}")
    elif len(args) == 1:
        print(f"{address}: {args[0]}")
    else:
        print(f"{address}: {args}")


def parse_osc_command(command):
    try:
        parts = shlex.split(command)
    except ValueError as e:
        logger.exception(f"Failed to parse command")
        return None, []

    if not parts:
        return None, []

    address = parts[0]
    arguments = parts[1:]

    return address, arguments


def start_osc_server(host, port, disp):
    server = osc_server.ThreadingOSCUDPServer(
        (host, port),
        disp
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()
    logger.debug(f"Listening for OSC messages on {host} {port}")
    print(f"Listening for OSC messages on {host} {port}")

    return server, thread


def stop_osc_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join()
    logger.debug("OSC Server stopped")


def create_osc_client(host, port):
    client = udp_client.SimpleUDPClient(host, port)
    logger.debug(f"Created sender for {host} {port}")
    print(f"Sending to {host} {port}")
    return client
