"""Module utils -- some useful classes or functions.

"""
# pyright: strict

from dataclasses import fields
from typing import TypeVar

MILLION = 1000000


def div(a: float, b: float) -> float:
    """
    Percentage calculations usually imply a division. For some municipalities, however,
    the data may be incomplete or irrelevant and the denominator happens to be zero.
    In this case, a result of 0 is returned, also to avoid an exception.
    """
    return 0.0 if b == 0.0 else a / b


T = TypeVar("T")


def element_wise_plus(a: T, b: T) -> T:
    """Element wise addition for a dataclasses"""
    return type(a)(*(getattr(a, f.name) + getattr(b, f.name) for f in fields(a)))
