"""UUID transform plugin module"""

import os
import re
import uuid
from collections.abc import Sequence

import uuid6
from cmem_plugin_base.dataintegration.description import Plugin, PluginParameter
from cmem_plugin_base.dataintegration.plugins import TransformPlugin
from cmem_plugin_base.dataintegration.types import BoolParameterType

from cmem_plugin_uuid.utils import (
    UUID_V3,
    UUID_V5,
    clock_seq_to_int,
    get_namespace_uuid,
    namespace_hex,
    node_to_int,
    repeat_for_inputs,
    uuid3_uuid5_namespace_param,
    uuid_convert_param_in,
    uuid_convert_param_out,
)


def uuid8(a: int | None = None, b: int | None = None, c: int | None = None) -> uuid.UUID:
    """Generate a UUIDv8 from three custom blocks (RFC 9562 §5.8).

    Backport of ``uuid.uuid8`` from the Python 3.14 standard library. Once this
    project moves to Python 3.14, this function is obsolete and ``uuid.uuid8``
    from the stdlib will be used directly.

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


_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_URN_PATTERN = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


@Plugin(
    label="UUIDv1",
    categories=["Value", "Identifier"],
    description="Generate a UUIDv1 from a host ID, sequence number, and the current time",
    documentation="""
UUIDv1 is generated from a host ID, sequence number, and the current
time.

""",
    parameters=[
        PluginParameter(
            name="node",
            label="Node (default: hardware address)",
            description=(
                'Node value in the form "01:23:45:67:89:AB", 01-23-45-67-89-AB", or '
                '"0123456789AB". If not given, it is attempted to obtain the hardware '
                "address. If this is unsuccessful, a random 48-bit number is chosen."
            ),
            default_value=None,
        ),
        PluginParameter(
            name="clock_seq",
            label="Clock sequence (default: random)",
            description=(
                "If clock sequence is given, it is used as the sequence number. "
                "Otherwise a random 14-bit sequence number is chosen."
            ),
            default_value=None,
        ),
    ],
)
class UUID1(TransformPlugin):
    """UUID1 Transform Plugin"""

    def __init__(
        self,
        node: str,
        clock_seq: str,
    ):
        self.node = node_to_int(node) if node else None
        self.clock_seq = clock_seq_to_int(clock_seq) if clock_seq else None

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        return repeat_for_inputs(
            inputs, lambda: str(uuid.uuid1(node=self.node, clock_seq=self.clock_seq))
        )


@Plugin(
    label="UUIDv3",
    categories=["Value", "Identifier"],
    description="Generate a UUIDv3",
    documentation="""UUID3 is based on the MD5 hash of a namespace identifier (which
    is a UUID) and a name (which is a string).""",
    parameters=[
        PluginParameter(
            param_type=uuid3_uuid5_namespace_param,
            name="namespace",
            label="Namespace",
            description="The namespace.",
            default_value="",
        ),
        PluginParameter(
            param_type=BoolParameterType(),
            name="namespace_as_uuid",
            label="Namespace as UUID",
            description=(
                "Applies only if none of the pre-defined namespaces is selected. If "
                "enabled, the namespace string needs to be a valid UUID. "
                "Otherwise, the namespace UUID is a UUIDv1 derived from the MD5 hash "
                "of the namespace string."
            ),
            default_value=False,
        ),
    ],
)
class UUID3(TransformPlugin):
    """UUID3 Transform Plugin"""

    def __init__(
        self,
        namespace: str,
        namespace_as_uuid: bool | None,
    ):
        self.namespace = namespace
        self.namespace_as_uuid = namespace_as_uuid

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        namespace_uuid = get_namespace_uuid(
            namespace_as_uuid=self.namespace_as_uuid,
            namespace=self.namespace,
            uuid_version=UUID_V3,
        )
        result = []
        if inputs:
            for collection in inputs:
                for value in collection:
                    if not self.namespace.strip():
                        result += [
                            str(uuid.UUID(hex=namespace_hex(value, UUID_V3), version=UUID_V3))
                        ]
                    else:
                        result += [str(uuid.uuid3(namespace_uuid, value))]  # type: ignore[arg-type]
        return result


@Plugin(
    label="UUIDv4",
    categories=["Value", "Identifier"],
    description="Generate a random UUIDv4.",
    documentation="""UUIDv4 specifies a random UUID.""",
)
class UUID4(TransformPlugin):
    """UUID4 Transform Plugin"""

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        return repeat_for_inputs(inputs, lambda: str(uuid.uuid4()))


@Plugin(
    label="UUIDv5",
    categories=["Value", "Identifier"],
    description="Generate a UUIDv5",
    documentation="""UUID5 is based on the SHA1 hash of a namespace identifier (which
    is a UUID) and a name (which is a string).""",
    parameters=[
        PluginParameter(
            param_type=uuid3_uuid5_namespace_param,
            name="namespace",
            label="Namespace",
            description="If 'namespace' is not given, the input string is used.",
            default_value="",
        ),
        PluginParameter(
            param_type=BoolParameterType(),
            name="namespace_as_uuid",
            label="Namespace as UUID",
            description=(
                "Applies only if none of the pre-defined namespaces is selected. If "
                "enabled, the namespace string needs to be a valid UUID. "
                "Otherwise, the namespace UUID is a UUIDv1 derived from the SHA1 hash "
                "of the namespace string."
            ),
            default_value=False,
        ),
    ],
)
class UUID5(TransformPlugin):
    """UUID5 Transform Plugin"""

    def __init__(
        self,
        namespace: str,
        namespace_as_uuid: bool | None,
    ):
        self.namespace = namespace
        self.namespace_as_uuid = namespace_as_uuid

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        namespace_uuid = get_namespace_uuid(
            namespace_as_uuid=self.namespace_as_uuid,
            namespace=self.namespace,
            uuid_version=UUID_V5,
        )
        result = []
        if inputs:
            for collection in inputs:
                for value in collection:
                    if not self.namespace.strip():
                        result += [
                            str(uuid.UUID(hex=namespace_hex(value, UUID_V5), version=UUID_V5))
                        ]
                    else:
                        result += [str(uuid.uuid5(namespace_uuid, value))]  # type: ignore[arg-type]
        return result


@Plugin(
    label="UUIDv6",
    categories=["Value", "Identifier"],
    description="Generate a UUIDv6 from a host ID, sequence number, and the current time",
    documentation="""
UUIDv6 is generated from a host ID, sequence number, and the current
time.

UUIDv6 is a field-compatible version of UUIDv1, reordered for
improved DB locality. It is expected that UUIDv6 will primarily be
used in contexts where there are existing v1 UUIDs. Systems that do
not involve legacy UUIDv1 SHOULD consider using UUIDv7 instead.
""",
    parameters=[
        PluginParameter(
            name="node",
            label="Node (default: hardware address)",
            description=(
                'Node value in the form "01:23:45:67:89:AB", 01-23-45-67-89-AB", or '
                '"0123456789AB". If not given, a random 48-bit number is chosen.'
            ),
            default_value="",
        ),
        PluginParameter(
            name="clock_seq",
            label="Clock sequence (default: random)",
            description=(
                "If clock sequence is given, it is used as the sequence number. "
                "Otherwise a random 14-bit number is chosen."
            ),
            default_value="",
        ),
    ],
)
class UUID6(TransformPlugin):
    """UUID6 Transform Plugin"""

    def __init__(
        self,
        node: str,
        clock_seq: str,
    ):
        self.node = node_to_int(node) if node else None
        self.clock_seq = clock_seq_to_int(clock_seq) if clock_seq else None

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        return repeat_for_inputs(
            inputs, lambda: str(uuid6.uuid6(node=self.node, clock_seq=self.clock_seq))
        )


@Plugin(
    label="UUIDv1 to UUIDv6",
    categories=["Value", "Identifier"],
    description="Generate UUIDv6 from a UUIDv1.",
    documentation="""
UUIDv6 is a field-compatible version of UUIDv1, reordered for
improved DB locality. It is expected that UUIDv6 will primarily be
used in contexts where there are existing v1 UUIDs. Systems that do
not involve legacy UUIDv1 SHOULD consider using UUIDv7 instead.
""",
)
class UUID1ToUUID6(TransformPlugin):
    """UUID1 to UUID6 Transform Plugin"""

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        result = []
        if inputs:
            for collection in inputs:
                for value in collection:
                    try:
                        result += [str(uuid6.uuid1_to_uuid6(uuid.UUID(value)))]
                    except ValueError as exc:
                        raise ValueError(f"{value} is not a valid UUIDv1 string") from exc
        return result


@Plugin(
    label="UUIDv7",
    categories=["Value", "Identifier"],
    description="Generate a UUIDv7 from a random number, and the current time.",
    documentation="""UUIDv7 features a time-ordered value field derived from the
widely implemented and well known Unix Epoch timestamp source, the
number of milliseconds since midnight 1 Jan 1970 UTC, leap seconds
excluded. As well as improved entropy characteristics over versions
1 or 6.
Implementations SHOULD utilize UUIDv7 over UUIDv1 and
6 if possible.
""",
)
class UUID7(TransformPlugin):
    """UUID7 Transform Plugin"""

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        return repeat_for_inputs(inputs, lambda: str(uuid6.uuid7()))


@Plugin(
    label="UUIDv8",
    categories=["Value", "Identifier"],
    description="Generate a UUIDv8 from three custom data fields (RFC 9562 §5.8).",
    documentation="""UUIDv8 is a free-form / experimental UUID format defined in
RFC 9562 §5.8. The 122 bits available outside the version and variant fields
are split into three custom data fields: 'a' (48 bits, octets 0-5), 'b' (12
bits, octets 6-7), and 'c' (62 bits, octets 8-15). When a field is left
empty, a random value is used.
""",
    parameters=[
        PluginParameter(
            name="a",
            label="Custom data 'a' (default: random)",
            description=(
                "First 48-bit chunk of the UUID (octets 0-5) as a positive integer. "
                "If not given, a random value is used."
            ),
            default_value="",
        ),
        PluginParameter(
            name="b",
            label="Custom data 'b' (default: random)",
            description=(
                "Middle 12-bit chunk of the UUID (octets 6-7) as a positive integer. "
                "If not given, a random value is used."
            ),
            default_value="",
        ),
        PluginParameter(
            name="c",
            label="Custom data 'c' (default: random)",
            description=(
                "Last 62-bit chunk of the UUID (octets 8-15) as a positive integer. "
                "If not given, a random value is used."
            ),
            default_value="",
        ),
    ],
)
class UUID8(TransformPlugin):
    """UUID8 Transform Plugin"""

    def __init__(self, a: str = "", b: str = "", c: str = ""):
        self.a = self._parse_field("a", a, 48) if a else None
        self.b = self._parse_field("b", b, 12) if b else None
        self.c = self._parse_field("c", c, 62) if c else None

    @staticmethod
    def _parse_field(name: str, value: str, bits: int) -> int:
        """Parse and range-check a UUID8 custom data field."""
        try:
            parsed = int(value)
        except ValueError as exc:
            raise ValueError(f"{name}: not a valid integer ({value})") from exc
        if not 0 <= parsed < (1 << bits):
            raise ValueError(f"{name}: must be a {bits}-bit non-negative integer ({value})")
        return parsed

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        return repeat_for_inputs(inputs, lambda: str(uuid8(self.a, self.b, self.c)))


@Plugin(
    label="UUID Convert",
    categories=["Value", "Identifier"],
    description="Convert a UUID string representation",
    documentation="""Convert a UUID string with 32 hexadecimal digits to a 16-byte
    string containing the six integer fields in big-endian byte order, a 16-byte string
    the six integer fields in little-endian byte order, a 32-character lowercase
    hexadecimal string, a 128-bit integer, or a URN. Strings in the correct format,
    however, the log will show a warning if the input does not comply with the standard
    specified in RFC 4122 and the proposed updates""",
    parameters=[
        PluginParameter(
            param_type=uuid_convert_param_in,
            name="from_format",
            label="From",
            description="Input string format",
            default_value="uuid_hex",
        ),
        PluginParameter(
            param_type=uuid_convert_param_out,
            name="to_format",
            label="To",
            description="Output string format",
            default_value="hex",
        ),
    ],
)
class UUIDConvert(TransformPlugin):
    """Converts UUID representation"""

    def __init__(self, from_format: str = "uuid_hex", to_format: str = "hex") -> None:
        self.from_ = from_format
        self.to = to_format

    def _parse_input(self, uuid_string: str) -> uuid.UUID:
        """Parse ``uuid_string`` according to ``self.from_``."""
        match self.from_:
            case "uuid_hex":
                try:
                    return uuid.UUID(uuid_string)
                except ValueError as exc:
                    raise ValueError(f"{uuid_string} is not a valid 32-bit UUID string") from exc
            case "int":
                try:
                    return uuid.UUID(int=int(uuid_string))
                except ValueError as exc:
                    raise ValueError(
                        f"{uuid_string} is not a valid 128-bit integer UUID value"
                    ) from exc
            case "urn":
                normalized = uuid_string.lower()
                if not _URN_PATTERN.match(normalized):
                    raise ValueError(f"{uuid_string} is not a valid UUID URN")
                return uuid.UUID(normalized)
            case _:
                raise ValueError(f"Unknown input format: {self.from_}")

    def _format_output(self, in_uuid: uuid.UUID) -> str:
        """Format ``in_uuid`` according to ``self.to``."""
        match self.to:
            case "uuid":
                return str(in_uuid)
            case "hex":
                return str(in_uuid.hex)
            case "int":
                return str(in_uuid.int)
            case "urn":
                return str(in_uuid.urn)
            case _:
                raise ValueError(f"Unknown output format: {self.to}")

    def convert_uuid(self, uuid_string: str) -> str:
        """Convert UUID string"""
        in_uuid = self._parse_input(uuid_string)
        if not _UUID_PATTERN.match(str(in_uuid)):
            self.log.warning(
                f"{uuid_string} is not a valid UUID as specified in RFC 4122 and "
                f"the proposed updates"
            )
        return self._format_output(in_uuid)

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        return [self.convert_uuid(value) for collection in inputs for value in collection]


@Plugin(
    label="UUID Version",
    categories=["Value", "Identifier"],
    description="Outputs UUID version number of input",
    documentation="""Input: UUID string, output: UUID version number of input.""",
)
class UUIDVersion(TransformPlugin):
    """Outputs UUID version number"""

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Transform"""
        return [str(uuid.UUID(value).version) for collection in inputs for value in collection]
