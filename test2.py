#! /usr/bin/env python3

def foo(a, b = 10 * 3):
    print("a:%s" % a)
    print("b:%s" % b)

foo(1)
foo(2,3)
