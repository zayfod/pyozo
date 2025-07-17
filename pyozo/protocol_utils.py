from typing import Any, List, Dict, Tuple, ClassVar, Union
from enum import Enum

import struct


__all__ = [
    "BinaryReader",
    "BinaryWriter",
    "FieldType",
    "FieldInfo",
    "Field",
    "BaseModelMeta",
    "BaseModel",
]


class BinaryReader:
    """Used to read in a stream of binary data, keeping track of the current position."""

    def __init__(self, buffer: Union[bytes, bytearray], offset: int = 0):
        self._buffer = buffer
        self._index = offset

    @property
    def buffer(self) -> bytes:
        return bytes(self._buffer)

    def __len__(self) -> int:
        return len(self._buffer)

    def seek_set(self, offset: int) -> None:
        if offset < 0 or offset > len(self._buffer):
            ValueError("Invalid offset.")
        self._index = offset

    def seek_cur(self, offset: int) -> None:
        offset += self._index
        if offset < 0 or offset > len(self._buffer):
            ValueError("Invalid offset.")
        self._index = offset

    def tell(self) -> int:
        """Returns the current stream position as an offset within the buffer."""
        return self._index

    def read(self, fmt: str) -> Any:
        """Reads in a single value of the given format."""
        reader = struct.Struct(f"<{fmt}")
        if self._index + reader.size > len(self._buffer):
            raise IndexError(
                "Buffer not large enough to read serialized message. Received {0} bytes.".format(len(self._buffer))
            )
        result = reader.unpack_from(self._buffer, self._index)[0]
        self._index += reader.size
        return result


class BinaryWriter:
    """Used to write out a stream of binary data."""

    def __init__(self) -> None:
        self._buffer: List[bytes] = []

    def __len__(self) -> int:
        return len(self._buffer)

    def clear(self) -> None:
        del self._buffer[:]

    def dumps(self) -> bytes:
        return b"".join(self._buffer)

    def write_bytes(self, value: bytes) -> None:
        """Writes out a byte sequence."""
        self._buffer.append(value)

    def write(self, value: Any, fmt: str) -> None:
        """Writes out a single value of the given format."""
        writer = struct.Struct(f"<{fmt}")
        self._buffer.append(writer.pack(value))


class FieldType(Enum):
    UINT8 = 1
    UINT16 = 2
    UINT32 = 3
    INT8 = 4
    INT16 = 5
    INT32 = 6
    FLOAT = 7  # 24-bit single-precision float.
    BYTES = 8  # Raw bytes. Only works as the last field.
    STRZ = 9  # NUL-terminated string. Only works as the last field.
    STR = 10  # String (used with file transfer service). Only works as the last field.


class FieldInfo:
    def __init__(self, field_type: FieldType, default: Any = ..., description: str = "") -> None:
        self.type: Any = None  # Actual type of the model member variable.
        self.field_type = field_type  # Encoding type.
        self.default = default  # Default value.
        self.description = description  # Field description.


def Field(field_type: FieldType, default: Any = ..., description: str = "") -> Any:
    return FieldInfo(field_type=field_type, default=default, description=description)


class BaseModelMeta(type):
    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> type:
        annotations = namespace.get("__annotations__", {})
        fields: Dict[str, FieldInfo] = {}

        for attr_name, attr_type in annotations.items():
            if attr_name == "_fields":
                continue
            field_info = namespace.get(attr_name, ...)
            if not isinstance(field_info, FieldInfo):
                raise TypeError(f"Field '{attr_name}' must be an instance of Field.")
            field_info.type = attr_type
            fields[attr_name] = field_info

        namespace["_fields"] = fields
        return super().__new__(mcs, name, bases, namespace)


def float_to_s24(f: float) -> int:
    res = round(f * 16777216)
    if res < (-2 * 1073741824) or res >= (2 * 1073741824):
        raise ValueError(f"Cannot convert {f} to S24. Value out of range.")
    return res


def s24_to_float(i: int) -> float:
    return float(i) / 16777216


class BaseModel(metaclass=BaseModelMeta):
    _fields: ClassVar[Dict[str, FieldInfo]] = {}

    def __init__(self, **kwargs: Any) -> None:
        for field_name, field_info in self._fields.items():
            if field_name in kwargs:
                value = kwargs[field_name]
            elif field_info.default is not ...:
                value = field_info.default
            else:
                raise TypeError(f"Missing required field '{field_name}'.")
            setattr(self, field_name, value)

    def get_size(self) -> int:
        """Returns the size in bytes of all fields."""
        size = 0
        for field, field_info in self._fields.items():
            if field_info.field_type == FieldType.UINT8:
                size += 1
            elif field_info.field_type == FieldType.UINT16:
                size += 2
            elif field_info.field_type == FieldType.UINT32:
                size += 4
            elif field_info.field_type == FieldType.INT8:
                size += 1
            elif field_info.field_type == FieldType.INT16:
                size += 2
            elif field_info.field_type == FieldType.INT32:
                size += 4
            elif field_info.field_type == FieldType.FLOAT:
                size += 4
            elif field_info.field_type == FieldType.BYTES:
                value = getattr(self, field)
                size += len(value)
            elif field_info.field_type == FieldType.STRZ:
                value = getattr(self, field)
                size += len(value) + 1
            elif field_info.field_type == FieldType.STR:
                value = getattr(self, field)
                size += len(value)
            else:
                raise ValueError(f"Unsupported field type '{field_info.field_type}'.")
        return size

    def __len__(self) -> int:
        """Returns the size in bytes of all fields."""
        return self.get_size()

    def __repr__(self) -> str:
        fields = [f"{field}={getattr(self, field)}" for field in self._fields.keys()]
        res = f"{type(self).__name__}({', '.join(fields)})"
        return res

    def to_bytes(self) -> bytes:
        writer = BinaryWriter()
        self.to_writer(writer)
        return writer.dumps()

    def to_writer(self, writer: BinaryWriter) -> None:
        for field, field_info in self._fields.items():
            value = getattr(self, field, field_info.default)
            if isinstance(value, Enum):
                value = value.value
            if field_info.field_type == FieldType.UINT8:
                writer.write(value, "B")
            elif field_info.field_type == FieldType.UINT16:
                writer.write(value, "H")
            elif field_info.field_type == FieldType.UINT32:
                writer.write(value, "L")
            elif field_info.field_type == FieldType.INT8:
                writer.write(value, "b")
            elif field_info.field_type == FieldType.INT16:
                writer.write(value, "h")
            elif field_info.field_type == FieldType.INT32:
                writer.write(value, "l")
            elif field_info.field_type == FieldType.FLOAT:
                writer.write(float_to_s24(value), "l")
            elif field_info.field_type == FieldType.BYTES:
                writer.write_bytes(value)
            elif field_info.field_type == FieldType.STRZ:
                writer.write_bytes(value.encode("utf8"))
                writer.write(b"\0", "c")
            elif field_info.field_type == FieldType.STR:
                writer.write_bytes(value.encode("utf8"))
            else:
                raise ValueError(f"Unsupported field type '{field_info.field_type}'.")

    @classmethod
    def from_bytes(cls, buffer: Union[bytes, bytearray]) -> "BaseModel":
        reader = BinaryReader(buffer)
        obj = cls.from_reader(reader)
        return obj

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> "BaseModel":
        kwargs = {}
        for field_name, field_info in cls._fields.items():
            if field_info.field_type == FieldType.UINT8:
                value = reader.read("B")
            elif field_info.field_type == FieldType.UINT16:
                value = reader.read("H")
            elif field_info.field_type == FieldType.UINT32:
                value = reader.read("L")
            elif field_info.field_type == FieldType.INT8:
                value = reader.read("b")
            elif field_info.field_type == FieldType.INT16:
                value = reader.read("h")
            elif field_info.field_type == FieldType.INT32:
                value = reader.read("l")
            elif field_info.field_type == FieldType.FLOAT:
                value = reader.read("l")
                value = s24_to_float(value)
            elif field_info.field_type == FieldType.BYTES:
                value = reader.buffer[reader.tell() :]
            elif field_info.field_type == FieldType.STRZ:
                value = reader.buffer[reader.tell() : -1].decode("utf8")
            elif field_info.field_type == FieldType.STR:
                value = reader.buffer[reader.tell() :].decode("utf8")
            else:
                raise ValueError(f"Unsupported field type '{field_info.field_type}'.")
            if issubclass(field_info.type, Enum):
                value = field_info.type(value)
            kwargs[field_name] = value
        return cls(**kwargs)
