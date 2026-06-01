"""Utilities for cmem-plugin-uuid"""

import os
import uuid
from binascii import unhexlify
from collections import OrderedDict
from hashlib import md5, sha1

from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType

uuid3_uuid5_namespace_param = ChoiceParameterType(
    OrderedDict(
        {
            "namespace_url": "Namespace URL",
            "namespace_dns": "Namespace DNS",
            "namespace_oid": "Namespace OID",
            "namespace_x500": "Namespace X500",
            "": "",
        }
    ),
)


uuid3_uuid5_namespace_param.allow_only_autocompleted_values = False


uuid_convert_param_in = ChoiceParameterType(
    OrderedDict(
        {
            "uuid_hex": "UUID/32-char hexadecimal string",
            "int": "128-bit integer",
            "urn": "URN",
        }
    ),
)

uuid_convert_param_in.allow_only_autocompleted_values = True

uuid_convert_param_out = ChoiceParameterType(
    OrderedDict(
        {
            "uuid": "UUID",
            "hex": "32-character lowercase hexadecimal string",
            "int": "128-bit integer",
            "urn": "URN",
        }
    ),
)

uuid_convert_param_out.allow_only_autocompleted_values = True


def node_to_int(node: str) -> int:
    """Convert a string representation of a node byte array to an integer"""
    try:
        byte_string = node.replace(":", "").replace("-", "")
        byte_array = unhexlify(byte_string)
        return int.from_bytes(byte_array, byteorder="big", signed=False)
    except ValueError as exc:
        raise ValueError(f"node: {exc} ({node})") from exc


def clock_seq_to_int(clock_seq: str) -> int:
    """Convert a string representation of a clock_seq to an integer."""
    try:
        return int(clock_seq)
    except ValueError as exc:
        raise ValueError(f"clock_seq: {exc} ({clock_seq})") from exc


def namespace_hex(value: str, uuid_version: int) -> str | None:
    """Return hex string from input value"""
    hex_value = None
    if uuid_version == 3:  # noqa: PLR2004
        hex_value = md5(value.encode(), usedforsecurity=False).hexdigest()
    elif uuid_version == 5:  # noqa: PLR2004
        hex_value = sha1(value.encode(), usedforsecurity=False).hexdigest()[:32]
    return hex_value


def uuid8(a: int | None = None, b: int | None = None, c: int | None = None) -> uuid.UUID:
    """Generate a UUIDv8 from three custom blocks (RFC 9562 §5.8).

    Backport of ``uuid.uuid8`` from the Python 3.14 standard library. Once this
    project moves to Python 3.14 (when cmem switches), this function is
    obsolete and callers should use ``uuid.uuid8`` from the stdlib directly.

    * ``a`` is the first 48-bit chunk of the UUID (octets 0-5);
    * ``b`` is the mid 12-bit chunk (octets 6-7);
    * ``c`` is the last 62-bit chunk (octets 8-15).

    When a value is not specified, a pseudo-random value is generated.

    The version and variant bits are set manually rather than via
    ``UUID(version=8)`` because Python's stdlib ``UUID`` constructor rejects
    versions outside 1-5 prior to Python 3.14.
    """
    if a is None:
        a = int.from_bytes(os.urandom(6))
    if b is None:
        b = int.from_bytes(os.urandom(2)) & 0xFFF
    if c is None:
        c = int.from_bytes(os.urandom(8)) & 0x3FFFFFFFFFFFFFFF
    int_uuid_8 = (a & 0xFFFFFFFFFFFF) << 80
    int_uuid_8 |= (b & 0xFFF) << 64
    int_uuid_8 |= c & 0x3FFFFFFFFFFFFFFF
    # Set variant to RFC 4122/9562 ('10' at bits 62-63).
    int_uuid_8 &= ~(0xC000 << 48)
    int_uuid_8 |= 0x8000 << 48
    # Set version 8 (at bits 76-79).
    int_uuid_8 &= ~(0xF000 << 64)
    int_uuid_8 |= 8 << 76
    return uuid.UUID(int=int_uuid_8)


def get_namespace_uuid(
    namespace_as_uuid: bool | None,
    namespace: str,
    uuid_version: int,
) -> uuid.UUID | None:
    """Return namespace UUID"""
    namespace_uuid = None

    if namespace == "namespace_url":
        namespace_uuid = uuid.NAMESPACE_URL
    elif namespace == "namespace_dns":
        namespace_uuid = uuid.NAMESPACE_DNS
    elif namespace == "namespace_oid":
        namespace_uuid = uuid.NAMESPACE_OID
    elif namespace == "namespace_x500":
        namespace_uuid = uuid.NAMESPACE_X500
    elif namespace.strip():
        if namespace_as_uuid:
            namespace_uuid = uuid.UUID(namespace)
        else:
            namespace_uuid = uuid.UUID(hex=namespace_hex(namespace, uuid_version), version=1)

    return namespace_uuid
