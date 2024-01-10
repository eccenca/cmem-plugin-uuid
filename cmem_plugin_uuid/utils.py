"""Utilities for cmem-plugin-uuid"""

import uuid
from hashlib import md5, sha1
from collections import OrderedDict
from binascii import unhexlify
from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType


uuid3_uuid5_namespace_param = ChoiceParameterType(
    OrderedDict(
        {
            "namespace_url": "Namespace URL",
            "namespace_dns": "Namespace DNS",
            "namespace_oid": "Namespace OID",
            "namespace_x500": "Namespace X500",
            "empty_value": "Empty value",
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


def node_to_int(node: str):
    """
    Convert a string representation of a node byte array to an integer.
    E.g. 01:23:45:67:89:AB -> 1250999896491
    """
    try:
        byte_string = node.replace(":", "").replace("-", "")
        byte_array = unhexlify(byte_string)
        return int.from_bytes(byte_array, byteorder="big", signed=False)
    except Exception as exc:
        raise ValueError(f"node: {exc} ({node})") from exc


def clock_seq_to_int(clock_seq: str):
    """Convert a string representation of a clock_seq to an integer."""
    try:
        return int(clock_seq)
    except Exception as exc:
        raise ValueError(f"clock_seq: {exc} ({clock_seq})") from exc


def namespace_hex(value, uuid_version):
    """
    Return hex string from input value
    """
    hex_value = None
    if uuid_version == 3:
        hex_value = md5(value.encode(), usedforsecurity=False).hexdigest()
    elif uuid_version == 5:
        hex_value = sha1(value.encode(), usedforsecurity=False).hexdigest()[:32]
    return hex_value


def get_namespace_uuid(
    namespace_as_uuid=None,
    namespace=None,
    uuid_version=None,
):
    """returns namespace UUID"""

    namespace_uuid = None

    if namespace == "namespace_url":
        namespace_uuid = uuid.NAMESPACE_URL
    elif namespace == "namespace_dns":
        namespace_uuid = uuid.NAMESPACE_DNS
    elif namespace == "namespace_oid":
        namespace_uuid = uuid.NAMESPACE_OID
    elif namespace == "namespace_x500":
        namespace_uuid = uuid.NAMESPACE_X500
    elif namespace != "empty_value":
        if namespace_as_uuid:
            namespace_uuid = uuid.UUID(namespace)
        else:
            namespace_uuid = uuid.UUID(
                hex=namespace_hex(namespace, uuid_version), version=1
            )

    return namespace_uuid
