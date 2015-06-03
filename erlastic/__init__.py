
"""Erlang External Term Format serializer/deserializer"""

__version__ = "2.0.0"
__license__ = "BSD"

from erlastic.codec import ErlangTermDecoder, ErlangTermEncoder
from erlastic.types import *

encode = ErlangTermEncoder().encode
decode = ErlangTermDecoder().decode

import struct
import sys
def mailbox_gen():
  while True:
    len_bin = sys.stdin.buffer.read(4)
    if len(len_bin) != 4: return None
    (length,) = struct.unpack('!I',len_bin)
    yield decode(sys.stdin.buffer.read(length))
def port_gen():
  while True:
    term = encode((yield))
    sys.stdout.buffer.write(struct.pack('!I',len(term)))
    sys.stdout.buffer.write(term)
def port_connection():
  port = port_gen()
  next(port)
  return mailbox_gen(),port
