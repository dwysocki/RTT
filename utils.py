import socket

def mod256(x):
    """Finds `x` modulus 256"""
    return x % 256

def makebytes(n):
    """Makes a byte object with `n` bytes. Each successive byte is the increment
    of the last, modulo 256"""
    return bytes(map(mod256,
                     range(n)))

def get_bit(number, N):
    """Returns whether the `N`th bit from `number` is set."""
    return bool(number & (1 << N))

type_map = {'TCP' : socket.SOCK_STREAM,
            'UDP' : socket.SOCK_DGRAM}
