def mod256(x):
    """Finds x modulus 256"""
    return x % 256

def makebytes(n):
    """Makes a byte object with n bytes. Each successive byte is the increment
    of the last, modulo 256"""
    return bytes(map(mod256,
                     range(n)))
