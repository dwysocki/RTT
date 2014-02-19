def do_tests(test, host, port, iter):
    """Perform the given test on the given host and port for each item in
    iter. test must be a function with arguments (host, port, x), where x
    will be given the item from iter.
    """
    test = lambda x: test(host, port, x)
    return {x : test(x) for x in iter}
