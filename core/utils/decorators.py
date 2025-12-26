# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Decorators

This module provides utility decorators for various purposes.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"


def singleton(cls):
    """
    A decorator that transforms a class into a Singleton.

    This decorator ensures only one instance of the decorated class is created.
    Subsequent calls to the class constructor will return the same instance.

    Usage::
        @singleton
        class MyClass:
            ...

    :param cls: The class to be decorated as a Singleton.
    :return: The decorated class, which is a Singleton.
    """

    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    get_instance.__wrapped__ = cls

    return get_instance
