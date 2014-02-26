import socket

def mod256(x):
    """Finds x modulus 256"""
    return x % 256

def makebytes(n):
    """Makes a byte object with n bytes. Each successive byte is the increment
    of the last, modulo 256"""
    return bytes(map(mod256,
                     range(n)))

def get_bit(decimal, N):
    """Returns the `N`th bit from `decimal`"""
    constant = 1 << (N-1)
    return decimal & constant

type_map = {'TCP' : socket.SOCK_STREAM,
            'UDP' : socket.SOCK_DGRAM}
