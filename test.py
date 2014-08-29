from functools import wraps

def wrapper(func):
    @wraps(func)
    def wrapped(*args):
        print 'hello'
        print 'args are', args
        func(*args)
    return wrapped

@wrapper
def test(a, b):
    print a, b 

if __name__ == "__main__":
    test(5, 6)
