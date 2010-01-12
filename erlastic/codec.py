
from __future__ import division

import struct

from erlastic.constants import *
from erlastic.types import *

__all__ = ["ErlangTermEncoder", "ErlangTermDecoder", "EncodingError"]

class EncodingError(Exception):
    pass

class ErlangTermDecoder(object):
    def __init__(self, encoding=None):
        self.encoding = encoding
        # Cache decode functions to avoid having to do a getattr
        self.decoders = {}
        for k in self.__class__.__dict__:
            v = getattr(self, k)
            if callable(v) and k.startswith('decode_'):
                self.decoders[k.split('_')[1]] = v

    def decode(self, bytes, offset=0):
        version = ord(bytes[offset])
        if version != FORMAT_VERSION:
            raise EncodingError("Bad version number. Expected %d found %d" % (FORMAT_VERSION, version))
        return self.decode_part(bytes, offset+1)[0]

    def decode_part(self, bytes, offset=0):
        return self.decoders[bytes[offset]](bytes, offset+1)

    def decode_a(self, bytes, offset):
        """SMALL_INTEGER_EXT"""
        return ord(bytes[offset]), offset+1

    def decode_b(self, bytes, offset):
        """INTEGER_EXT"""
        return struct.unpack(">l", bytes[offset:offset+4])[0], offset+4

    def decode_c(self, bytes, offset):
        """FLOAT_EXT"""
        return float(bytes[offset:offset+31].split('\x00', 1)[0]), offset+31

    def decode_F(self, bytes, offset):
        """NEW_FLOAT_EXT"""
        return struct.unpack(">d", bytes[offset:offset+8])[0], offset+8

    def decode_d(self, bytes, offset):
        """ATOM_EXT"""
        atom_len = struct.unpack(">H", bytes[offset:offset+2])[0]
        atom = bytes[offset+2:offset+2+atom_len]
        return self.convert_atom(atom), offset+atom_len+2

    def decode_s(self, bytes, offset):
        """SMALL_ATOM_EXT"""
        atom_len = ord(bytes[offset])
        atom = bytes[offset+1:offset+1+atom_len]
        return self.convert_atom(atom), offset+atom_len+1

    def decode_h(self, bytes, offset):
        """SMALL_TUPLE_EXT"""
        arity = ord(bytes[offset])
        offset += 1

        items = []
        for i in range(arity):
            val, offset = self.decode_part(bytes, offset)
            items.append(val)
        return tuple(items), offset

    def decode_i(self, bytes, offset):
        """LARGE_TUPLE_EXT"""
        arity = struct.unpack(">L", bytes[offset:offset+4])[0]
        offset += 4

        items = []
        for i in range(arity):
            val, offset = self.decode_part(bytes, offset)
            items.append(val)
        return tuple(items), offset

    def decode_j(self, bytes, offset):
        """NIL_EXT"""
        return [], offset

    def decode_k(self, bytes, offset):
        """STRING_EXT"""
        length = struct.unpack(">H", bytes[offset:offset+2])[0]
        st = bytes[offset+2:offset+2+length]
        if self.encoding:
            try:
                st = st.decode(self.encoding)
            except UnicodeError:
                st = [ord(x) for x in st]
        else:
            st = [ord(x) for x in st]
        return st, offset+2+length

    def decode_l(self, bytes, offset):
        """LIST_EXT"""
        length = struct.unpack(">L", bytes[offset:offset+4])[0]
        offset += 4
        items = []
        for i in range(length):
            val, offset = self.decode_part(bytes, offset)
            items.append(val)
        tail, offset = self.decode_part(bytes, offset)
        if tail != []:
            # TODO: Not sure what to do with the tail
            raise NotImplementedError("Lists with non empty tails are not supported")
        return items, offset

    def decode_m(self, bytes, offset):
        """BINARY_EXT"""
        length = struct.unpack(">L", bytes[offset:offset+4])[0]
        return bytes[offset+4:offset+4+length], offset+4+length

    def decode_n(self, bytes, offset):
        """SMALL_BIG_EXT"""
        n = ord(bytes[offset])
        offset += 1
        return self.decode_bigint(n, bytes, offset)

    def decode_o(self, bytes, offset):
        """LARGE_BIG_EXT"""
        n = struct.unpack(">L", bytes[offset:offset+4])[0]
        offset += 4
        return self.decode_bigint(n, bytes, offset)

    def decode_bigint(self, n, bytes, offset):
        sign = ord(bytes[offset])
        offset += 1
        b = 1
        val = 0
        for i in range(n):
            val += ord(bytes[offset]) * b
            b <<= 8
            offset += 1
        if sign != 0:
            val = -val
        return val, offset

    def decode_e(self, bytes, offset):
        """REFERENCE_EXT"""
        node, offset = self.decode_part(bytes, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing REFERENCE_EXT, found %r instead" % node)
        reference_id, creation = struct.unpack(">LB", bytes[offset:offset+5])
        return Reference(node, [reference_id], creation), offset+5

    def decode_r(self, bytes, offset):
        """NEW_REFERENCE_EXT"""
        id_len = struct.unpack(">H", bytes[offset:offset+2])[0]
        node, offset = self.decode_part(bytes, offset+2)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing NEW_REFERENCE_EXT, found %r instead" % node)
        creation = ord(bytes[offset])
        reference_id = struct.unpack(">%dL" % id_len, bytes[offset+1:offset+1+4*id_len])
        return Reference(node, reference_id, creation), offset+1+4*id_len

    def decode_f(self, bytes, offset):
        """PORT_EXT"""
        node, offset = self.decode_part(bytes, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing PORT_EXT, found %r instead" % node)
        port_id, creation = struct.unpack(">LB", bytes[offset:offset+5])
        return Port(node, port_id, creation), offset+5

    def decode_g(self, bytes, offset):
        """PID_EXT"""
        node, offset = self.decode_part(bytes, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing PID_EXT, found %r instead" % node)
        pid_id, serial, creation = struct.unpack(">LLB", bytes[offset:offset+9])
        return PID(node, pid_id, serial, creation), offset+9

    def decode_q(self, bytes, offset):
        """EXPORT_EXT"""
        module, offset = self.decode_part(bytes, offset)
        if not isinstance(module, Atom):
            raise EncodingError("Expected atom while parsing EXPORT_EXT, found %r instead" % module)
        function, offset = self.decode_part(bytes, offset)
        if not isinstance(function, Atom):
            raise EncodingError("Expected atom while parsing EXPORT_EXT, found %r instead" % function)
        arity, offset = self.decode_part(bytes, offset)
        if not isinstance(arity, int):
            raise EncodingError("Expected integer while parsing EXPORT_EXT, found %r instead" % arity)
        return Export(module, function, arity), offset+1

    def convert_atom(self, atom):
        if atom == "true":
            return True
        elif atom == "false":
            return False
        elif atom == "none":
            return None
        return Atom(atom)

class ErlangTermEncoder(object):
    def __init__(self, encoding="utf-8", unicode_type="binary"):
        self.encoding = encoding
        self.unicode_type = unicode_type

    def encode(self, obj):
        return chr(FORMAT_VERSION) + "".join(self.encode_part(obj))

    def encode_part(self, obj):
        if obj is False:
            return [ATOM_EXT, struct.pack(">H", 5), "false"]
        elif obj is True:
            return [ATOM_EXT, struct.pack(">H", 4), "true"]
        elif obj is None:
            return [ATOM_EXT, struct.pack(">H", 4), "none"]
        elif isinstance(obj, (int, long)):
            if 0 <= obj <= 255:
                return [SMALL_INTEGER_EXT, chr(obj)]
            elif -2147483648 <= obj <= 2147483647:
                return [INTEGER_EXT, struct.pack(">l", obj)]
            else:
                sign = chr(obj < 0)
                obj = abs(obj)

                big_bytes = []
                while obj > 0:
                    big_bytes.append(chr(obj & 0xff))
                    obj >>= 8

                if len(big_bytes) < 256:
                    return [SMALL_BIG_EXT, chr(len(big_bytes)), sign] + big_bytes
                else:
                    return [LARGE_BIG_EXT, struct.pack(">L", len(big_bytes)), sign] + big_bytes
        elif isinstance(obj, float):
            floatstr = "%.20e" % obj
            return [FLOAT_EXT, floatstr + "\x00"*(31-len(floatstr))]
        elif isinstance(obj, Atom):
            return [ATOM_EXT, struct.pack(">H", len(obj)), obj]
        elif isinstance(obj, str):
            return [BINARY_EXT, struct.pack(">L", len(obj)), obj]
        elif isinstance(obj, unicode):
            return self.encode_unicode(obj)
        elif isinstance(obj, tuple):
            n = len(obj)
            if n < 256:
                bytes = [SMALL_TUPLE_EXT, chr(n)]
            else:
                bytes = [LARGE_TUPLE_EXT, struct.pack(">L", n)]
            for item in obj:
                bytes += self.encode_part(item)
            return bytes
        elif obj == []:
            return [NIL_EXT]
        elif isinstance(obj, list):
            bytes = [LIST_EXT, struct.pack(">L", len(obj))]
            for item in obj:
                bytes += self.encode_part(item)
            bytes.append(NIL_EXT) # list tail - no such thing in Python
            return bytes
        elif isinstance(obj, Reference):
            return [NEW_REFERENCE_EXT,
                struct.pack(">H", len(obj.ref_id)),
                ATOM_EXT, struct.pack(">H", len(obj.node)), obj.node,
                chr(obj.creation), struct.pack(">%dL" % len(obj.ref_id), *obj.ref_id)]
        elif isinstance(obj, Port):
            return [PORT_EXT,
                ATOM_EXT, struct.pack(">H", len(obj.node)), obj.node,
                struct.pack(">LB", obj.port_id, obj.creation)]
        elif isinstance(obj, PID):
           return [PID_EXT,
                ATOM_EXT, struct.pack(">H", len(obj.node)), obj.node,
                struct.pack(">LLB", obj.pid_id, obj.serial, obj.creation)]
        elif isinstance(obj, Export):
            return [EXPORT_EXT,
                ATOM_EXT, struct.pack(">H", len(obj.module)), obj.module,
                ATOM_EXT, struct.pack(">H", len(obj.function)), obj.function,
                SMALL_INTEGER_EXT, chr(obj.arity)]
        else:
            raise NotImplementedError("Unable to serialize %r" % obj)

    def encode_unicode(self, obj):
        if not self.encoding:
            return self.encode_part([ord(x) for x in obj])
        else:
            st = obj.encode(self.encoding)
            if self.unicode_type == "binary":
                return [BINARY_EXT, struct.pack(">L", len(st)), st]
            elif self.unicode_type == "str":
                return [STRING_EXT, struct.pack(">H", len(st)), st]
            else:
                raise TypeError("Unknown unicode encoding type %s" % self.unicode_type)
