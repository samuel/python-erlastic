
"""Erlang External Term Format serializer/deserializer"""

__version__ = "1.1.0"
__license__ = "BSD"

from erlastic.codec import ErlangTermDecoder, ErlangTermEncoder
from erlastic.types import *

encode = ErlangTermEncoder().encode
decode = ErlangTermDecoder().decode

