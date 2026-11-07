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
        with (patch_stdout()):
            while True:
                try:
                    command = session.prompt("oscterm>").strip()

                    if command[0] == '/':
                        #
                        # This is an OSC address.
                        #

                        address, arguments = parse_osc_command(command)

                        if address:
                            if client is not None:
                                client.send_message(address, arguments)
                            else:
                                print("Warning: OSC send destination not set")

                    else:
                        #
                        # This is not an OSC address. It must be a command.
                        #

                        try:
                            parts = shlex.split(command)
                            if parts[0] == 'exit':
                                break

                            elif parts[0] in ['listen', 'l']:
                                if len(parts) == 1:
                                    # The command was just the word listen.
                                    # Print the current listener settings.
                                    #

                                    if server is not None and thread is not None:
                                        print(f"{listen_host} {listen_port}")
                                    else:
                                        print(f"Not listening for OSC messages")

                                else:
                                    # The command is the word listen, followed by
                                    # arguments, so this is a command to set up a
                                    # new listener.

                                    if len(parts) == 2:
                                        # Only one argument has been specified, so we will assume
                                        # that it is a port number and will listen on 0.0.0.0,
                                        # which means all available network interfaces.
                                        #

                                        listen_host = '0.0.0.0'
                                        port_index = 1

                                    elif len(parts) == 3:
                                        # Two arguments were supplied, so the first is the host and
                                        # the second is the port number.
                                        #

                                        listen_host = parts[1]
                                        port_index = 2

                                    else:
                                        print("Invalid host and port")
                                        continue

                                    #
                                    # Create the listener
                                    #

                                    try:
                                        listen_port = int(parts[port_index])

                                    except ValueError:
                                        print(f"{parts[port_index]} is not a valid port (must be an integer between 0 and 65535)")
                                        continue

                                    if listen_port < 0 or listen_port > 65535:
                                        print(f"{parts[port_index]} is not a valid port (must be an integer between 0 and 65535)")
                                        continue

                                    # Shut down OSC server if one already exists
                                    if server is not None and thread is not None:
                                        stop_osc_server(server, thread)

                                    # Set up OSC server to start listening for messages
                                    try:
                                        server, thread = start_osc_server(listen_host, listen_port, disp)

                                    except OSError as e:
                                        if "address already in use" in str(e).lower():
                                            print("Error: Address already in use")
                                            server = None
                                            thread = None
                                        else:
                                            print(f"Error: {e}")

                            elif parts[0] in ['send', 's']:
                                if len(parts) == 1:
                                    # The command is just the word send, without any
                                    # arguments. Print the current send settings.
                                    #

                                    if client is not None:
                                        print(f"Sending to {send_host} {send_port}")
                                    else:
                                        print(f"OSC send destination not set")

                                else:
                                    # Arguments were supplied as well, so we need to
                                    # create a new sender.

                                    if len(parts) == 2:
                                        # Only one argument was supplied, so we will assume
                                        # that it is a port number and we will send to
                                        # localhost
                                        #

                                        send_host = 'localhost'
                                        port_index = 1

                                    elif len(parts) == 3:
                                        # Two arguments were supplied, so the first is the host and
                                        # the second is the port number.
                                        #

                                        send_host = parts[1]
                                        port_index = 2

                                    else:
                                        print("Invalid host and port")
                                        continue

                                    try:
                                        send_port = int(parts[port_index])

                                    except ValueError:
                                        print(f"{parts[port_index]} is not a valid port (must be an integer between 0 and 65535)")
                                        continue
                                        
                                    if send_port < 0 or send_port > 65535:
                                        print(f"{parts[port_index]} is not a valid port (must be an integer between 0 and 65535)")
                                        continue

                                    # Set up a client for sending OSC messages
                                    client = create_osc_client(
                                        host=send_host,
                                        port=send_port
                                    )

                            elif parts[0] in ['help', '?']:
                                print_help_message()

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
        print(f"{address} {args[0]}")
    else:
        print(f"{address} {args}")


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

    # Convert all arguments to correct types
    arguments = [string_value_to_proper_type(argument) for argument in arguments]

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
    logger.debug(f"Listening on {host} {port}")
    print(f"Listening on {host} {port}")

    return server, thread


def stop_osc_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join()
    logger.debug("OSC Server stopped")


def create_osc_client(host, port):
    client = udp_client.SimpleUDPClient(host, port)
    logger.debug(f"Sending to {host} {port}")
    print(f"Sending to {host} {port}")
    return client


def string_value_to_proper_type(value: str):
    value = value.strip()

    # Try Boolean
    if value == 'True':
        return True

    if value == 'False':
        return False

    # Try Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Try Float
    try:
        if '.' in value:
            return float(value)
    except ValueError:
        pass

    # If none of the above worked, return as a string
    return value


def print_help_message():
    help_text = """
----------------------------------------------------------
oscterm Commands Reference
------------------
help or ? - Prints this command reference message.
------------------
listen or l
- When the word listen (or the letter l) is entered without any
  arguments, it is treated as a request for the current
  OSC listener settings, which are printed.
- When listen (or l) is followed by a port number, a new listener
  is created using all network interfaces on that port.
- When listen (or l) is followed by a hostname (or IP address) and
  a port number, a new listener is created for that host/IP only
  on the specified port. 
- Example 1: listen 1375
- Example 2: listen localhost 1235
- Example 2: l 192.168.0.45 52000
------------------
send or s
- When the word send (or the letter s) is entered without any
  arguments, it is treated as a request for the current
  OSC send settings, which are printed.
- When send (or s) is followed by a port number, subsequent
  OSC messages will be sent to localhost on the specified port.
- When send (or s) is followed by a hostname (or IP address) and
  a port number, subsequent OSC messages will be sent to that host
  and port.`
- Example 1: send localhost 1375
- Example 2: s 1375
- Example 3: send 192.168.0.45 52000
------------------
exit
- Exits oscterm.
- Ctrl-D on the keyboard does the same thing.
----------------------------------------------------------
    """
    print(help_text)
