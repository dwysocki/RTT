import numpy

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
    return numpy.array([mean(x), std(x), min(x), max(x)])
