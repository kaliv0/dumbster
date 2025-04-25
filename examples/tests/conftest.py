from collections import namedtuple

x = namedtuple("Foo", ["name", "age"])


def Foo(name, age):
    return x(name, age)
