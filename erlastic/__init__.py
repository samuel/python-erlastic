
"""Erlang External Term Format serializer/deserializer"""

__version__ = "0.1"
__license__ = "BSD"

from erlastic.codec import ErlangTermDecoder, ErlangTermEncoder
from erlastic.types import *

def encode(obj):
    return ErlangTermEncoder().encode(obj)

def decode(obj):
    return ErlangTermDecoder().decode(obj)
