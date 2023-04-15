import socket
import sys
import errno
# import select

from typing import Optional

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234


class EmptyHeaderError(BaseException):
    pass


class WrongHeaderFormatError(BaseException):
    pass


def convert_msg(message: str) -> bytes:
    '''Convert string to protocol format.'''
    message = message.encode('utf-8')
    message_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
    return message_header + message


def receive_msg(sock: socket.socket, critical: bool = False) -> Optional[str]:
    _header = sock.recv(HEADER_LENGTH).decode('utf-8')
    if critical:
        if not len(_header):
            raise EmptyHeaderError(f'header:\"{_header}\"')
    if not _header.strip().isnumeric() or int(_header) < 0:
        raise WrongHeaderFormatError(f'header:\"{_header}\"')

    _length = int(_header)
    _msg = sock.recv(_length).decode('utf-8')

    return _msg


my_username = input('username: ')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# username = my_username.encode('utf-8')
# username_header = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')

'''Send your name to server.'''
client_socket.send(convert_msg(my_username))

while True:
    message = input(f"{my_username} > ")

    if message:
        # message = message.encode('utf-8')
        # message_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
        client_socket.send(convert_msg(message))

    # receive resp
    try:
        while True:
            username = receive_msg(client_socket, critical=True)
            if not username:
                print('connection closed by server')
                # client_socket.close()
                sys.exit()
            message = receive_msg(client_socket, critical=False)

            print(f'{username} > {message}')

    # What does it mean?
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('reading error', str(e))
            sys.exit()
        continue

    except Exception as e:
        print('General error:', str(e))
        sys.exit()

    # should we close the socket we used?
    finally:
        client_socket.close()

