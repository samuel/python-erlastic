
"""Erlang External Term Format serializer/deserializer"""

__version__ = "1.1.0"
__license__ = "BSD"

from erlastic.codec import ErlangTermDecoder, ErlangTermEncoder
from erlastic.types import *

encode = ErlangTermEncoder().encode
decode = ErlangTermDecoder().decode

import struct
import sys
def port_req():
  len_bin = sys.stdin.buffer.read(4)
  if len(len_bin) != 4: return None
  (length,) = struct.unpack('!I',len_bin)
  yield decode(sys.stdin.buffer.read(length))
  yield from port_req()
def port_res(term):
  term = encode(term)
  sys.stdout.buffer.write(struct.pack('!I',len(term)))
  sys.stdout.buffer.write(term)
