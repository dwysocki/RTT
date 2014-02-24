import socket

def mod256(x):
    """Finds x modulus 256"""
    return x % 256

def makebytes(n):
    """Makes a byte object with n bytes. Each successive byte is the increment
    of the last, modulo 256"""
    return bytes(map(mod256,
                     range(n)))

def mean(x):
    """Find the mean of an iterable of numbers."""
    n = len(x)
    return sum(x) / n if n is not 0 else None

def std(x):
    """Find the standard deviation of an iterable of numbers."""
    m = mean(x)
    n = len(x)
    dev = (i - m for i in x)
    dev2 = (i**2 for i in dev)

    return sum(dev2) / (n - 1)

def summary(x):
    """Returns a tuple containing the mean, std, min, and max of the input
    list.
    """
    return mean(x), std(x), min(x), max(x)

type_map = {'TCP' : socket.SOCK_STREAM,
            'UDP' : socket.SOCK_DGRAM}
