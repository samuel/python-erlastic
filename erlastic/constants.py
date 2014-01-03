
FORMAT_VERSION = 131

NEW_FLOAT_EXT = 70      # [Float64:IEEE float]
BIT_BINARY_EXT = 77     # [UInt32:Len, UInt8:Bits, Len:Data]
SMALL_INTEGER_EXT = 97  # [UInt8:Int]
INTEGER_EXT = 98        # [Int32:Int]
FLOAT_EXT = 99          # [31:Float String] Float in string format (formatted "%.20e", sscanf "%lf"). Superseded by NEW_FLOAT_EXT
ATOM_EXT = 100          # 100 [UInt16:Len, Len:AtomName] max Len is 255
REFERENCE_EXT = 101     # 101 [atom:Node, UInt32:ID, UInt8:Creation]
PORT_EXT = 102          # [atom:Node, UInt32:ID, UInt8:Creation]
PID_EXT = 103           # [atom:Node, UInt32:ID, UInt32:Serial, UInt8:Creation]
SMALL_TUPLE_EXT = 104   # [UInt8:Arity, N:Elements]
LARGE_TUPLE_EXT = 105   # [UInt32:Arity, N:Elements]
NIL_EXT = 106           # empty list
STRING_EXT = 107        # [UInt32:Len, Len:Characters]
LIST_EXT = 108          # [UInt32:Len, Elements, Tail]
BINARY_EXT = 109        # [UInt32:Len, Len:Data]
SMALL_BIG_EXT = 110     # [UInt8:n, UInt8:Sign, n:nums]
LARGE_BIG_EXT = 111     # [UInt32:n, UInt8:Sign, n:nums]
NEW_FUN_EXT = 112       # [UInt32:Size, UInt8:Arity, 16*Uint6-MD5:Uniq, UInt32:Index, UInt32:NumFree, atom:Module, int:OldIndex, int:OldUniq, pid:Pid, NunFree*ext:FreeVars]
EXPORT_EXT = 113        # [atom:Module, atom:Function, smallint:Arity]
NEW_REFERENCE_EXT = 114 # [UInt16:Len, atom:Node, UInt8:Creation, Len*UInt32:ID]
SMALL_ATOM_EXT = 115    # [UInt8:Len, Len:AtomName]
FUN_EXT = 117           # [UInt4:NumFree, pid:Pid, atom:Module, int:Index, int:Uniq, NumFree*ext:FreeVars]
COMPRESSED = 80         # [UInt4:UncompressedSize, N:ZlibCompressedData]
