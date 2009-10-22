
"""Erlang External Term Format serializer/deserializer"""

__version__ = "0.0.1"

from erlastic.codec import ErlangTermDecoder, ErlangTermEncoder, Atom, Binary

def encode(obj):
    return ErlangTermEncoder().encode(obj)

def decode(obj):
    return ErlangTermDecoder().decode(obj)
