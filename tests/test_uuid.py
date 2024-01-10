"""Plugin tests."""
import uuid
import uuid6
from hashlib import md5, sha1
from cmem_plugin_uuid.transform import (
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    UUID6,
    UUID1ToUUID6,
    UUID7,
    UUID8,
    UUIDConvert,
    UUIDVersion,
)


# Test UUID1


def test_uuid1_without_input():
    result = UUID1(
        node=None,
        clock_seq=None,
    ).transform(inputs=[])
    assert len(result) == 1
    for item in result:
        assert uuid.UUID(item).version == 1


def test_uuid1_with_value_input():
    input_values = [["input1"], ["input2"]]
    result = UUID1(
        node=None,
        clock_seq=None,
    ).transform(inputs=input_values)
    assert len(result) == 2
    for item in result:
        assert uuid.UUID(item).version == 1


def test_uuid1_with_parameter_setting():
    input_values = [["input1"], ["input2"]]
    result = UUID1(
        node="2001",
        clock_seq="1234",
    ).transform(inputs=input_values)
    assert len(result) == 2
    for item in result:
        assert uuid.UUID(item).version == 1


# Test UUID3


def test_uuid3_with_namespace_param_as_uuid():
    input_values = ["input1", "input2"]
    namespace = str(uuid.uuid1())
    result = UUID3(
        namespace=namespace,
        namespace_as_uuid=True,
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 3
        assert item == str(
            uuid.uuid3(namespace=uuid.UUID(namespace), name=input_values[i])
        )


def test_uuid3_with_namespace_param_as_string():
    input_values = ["input1", "input2"]
    namespace_str = "test"
    hex_value = md5(namespace_str.encode(), usedforsecurity=False).hexdigest()
    namespace = uuid.UUID(hex=hex_value, version=1)
    result = UUID3(
        namespace=namespace_str,
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 3
        assert item == str(uuid.uuid3(namespace=namespace, name=input_values[i]))


def test_uuid3_with_namespace_dns():
    input_values = ["input1", "input2"]
    result = UUID3(
        namespace="namespace_dns",
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 3
        assert item == str(
            uuid.uuid3(
                namespace=uuid.NAMESPACE_DNS,
                name=input_values[i],
            )
        )


def test_uuid3_with_namespace_url():
    input_values = ["input1", "input2"]
    result = UUID3(
        namespace="namespace_url",
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 3
        assert item == str(
            uuid.uuid3(
                namespace=uuid.NAMESPACE_URL,
                name=input_values[i],
            )
        )


def test_uuid3_with_namespace_oid():
    input_values = ["input1", "input2"]
    result = UUID3(
        namespace="namespace_oid",
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 3
        assert item == str(
            uuid.uuid3(
                namespace=uuid.NAMESPACE_OID,
                name=input_values[i],
            )
        )


def test_uuid3_with_namespace_x500():
    input_values = ["input1", "input2"]
    result = UUID3(
        namespace="namespace_x500",
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 3
        assert item == str(
            uuid.uuid3(
                namespace=uuid.NAMESPACE_X500,
                name=input_values[i],
            )
        )


def test_uuid3_with_empty_namespace():
    input_values = [["input1"]]
    result = UUID3(
        namespace="empty_value",
    ).transform(inputs=input_values)
    assert len(result) == 1
    assert result == [
        str(
            uuid.UUID(
                md5(input_values[0][0].encode(), usedforsecurity=False).hexdigest(),
                version=3,
            )
        )
    ]


# Test UUID4


def test_uuid4_without_input():
    result = UUID4().transform(inputs=[])
    for item in result:
        assert uuid.UUID(item).version == 4


def test_uuid4_with_input():
    result = UUID4().transform(inputs=[["input1"], ["input2"]])
    assert len(result) == 2
    for item in result:
        assert uuid.UUID(item).version == 4


# Test UUID5


def test_uuid5_with_namespace_param_as_uuid():
    input_values = ["input1", "input2"]
    namespace = str(uuid.uuid1())
    result = UUID5(
        namespace=namespace,
        namespace_as_uuid=True,
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 5
        assert item == str(
            uuid.uuid5(namespace=uuid.UUID(namespace), name=input_values[i])
        )


def test_uuid5_with_namespace_param_as_string():
    input_values = ["input1", "input2"]
    namespace_str = "test"
    hex_value = sha1(namespace_str.encode(), usedforsecurity=False).hexdigest()[:32]
    namespace = uuid.UUID(hex=hex_value, version=1)
    result = UUID5(
        namespace=namespace_str,
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 5
        assert item == str(uuid.uuid5(namespace=namespace, name=input_values[i]))


def test_uuid5_with_namespace_dns():
    input_values = ["input1", "input2"]
    result = UUID5(
        namespace="namespace_dns",
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 5
        assert item == str(
            uuid.uuid5(
                namespace=uuid.NAMESPACE_DNS,
                name=input_values[i],
            )
        )


def test_uuid5_with_namespace_url():
    input_values = ["input1", "input2"]
    result = UUID5(
        namespace="namespace_url",
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 5
        assert item == str(
            uuid.uuid5(
                namespace=uuid.NAMESPACE_URL,
                name=input_values[i],
            )
        )


def test_uuid5_with_namespace_oid():
    input_values = ["input1", "input2"]
    result = UUID5(
        namespace="namespace_oid",
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 5
        assert item == str(
            uuid.uuid5(
                namespace=uuid.NAMESPACE_OID,
                name=input_values[i],
            )
        )


def test_uuid5_with_namespace_x500():
    input_values = ["input1", "input2"]
    result = UUID5(
        namespace="namespace_x500",
    ).transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 5
        assert item == str(
            uuid.uuid5(
                namespace=uuid.NAMESPACE_X500,
                name=input_values[i],
            )
        )


def test_uuid5_with_empty_namespace():
    input_values = [["input1"]]
    result = UUID5(
        namespace="empty_value",
    ).transform(inputs=input_values)
    assert len(result) == 1
    assert result == [
        str(
            uuid.UUID(
                sha1(input_values[0][0].encode(), usedforsecurity=False).hexdigest()[
                    :32
                ],
                version=5,
            )
        )
    ]


# Test UUID6


def test_uuid6_without_input():
    result = UUID6(
        node=None,
        clock_seq=None,
    ).transform(inputs=[])
    assert len(result) == 1
    for item in result:
        assert uuid.UUID(item).version == 6


def test_uuid6_with_value_input():
    input_values = [["input1"], ["input2"]]
    result = UUID6(
        node=None,
        clock_seq=None,
    ).transform(inputs=input_values)
    assert len(result) == 2
    for item in result:
        assert uuid.UUID(item).version == 6


def test_uuid6_with_parameter_setting():
    input_values = [["input1"], ["input2"]]
    result = UUID6(
        node="2001",
        clock_seq="1234",
    ).transform(inputs=input_values)
    assert len(result) == 2
    for item in result:
        assert uuid.UUID(item).version == 6


# Test UUID1ToUUID6


def test_uuid1_to_uuid6_with_input():
    input_values = [str(uuid.uuid1()), str(uuid.uuid1())]
    result = UUID1ToUUID6().transform(inputs=[[i] for i in input_values])
    assert len(result) == 2
    for i, item in enumerate(result):
        assert uuid.UUID(item).version == 6
        assert item == str(uuid6.uuid1_to_uuid6(uuid.UUID(input_values[i])))


# Test UUID7


def test_uuid7_without_input():
    result = UUID7().transform(inputs=[])
    assert len(result) == 1
    for item in result:
        assert uuid.UUID(item).version == 7


def test_uuid7_with_input():
    result = UUID7().transform(inputs=[["input1"], ["input2"]])
    assert len(result) == 2
    for item in result:
        assert uuid.UUID(item).version == 7


# Test UUID8


def test_uuid8_without_input():
    result = UUID8().transform(inputs=[])
    for item in result:
        assert uuid.UUID(item).version == 8


def test_uuid8_with_input():
    result = UUID8().transform(inputs=[["input1"], ["input2"]])
    assert len(result) == 2
    for item in result:
        assert uuid.UUID(item).version == 8


# Test UUIDConvert


def test_uuid_convert_to_uuid():
    test_uuid = uuid.uuid4()
    input_values = [str(test_uuid)]
    result = UUIDConvert(from_format="uuid_hex", to_format="uuid").transform(
        inputs=[input_values]
    )
    assert result == [str(test_uuid)]


def test_uuid_convert_to_hex():
    test_uuid = uuid.uuid4()
    input_values = [str(test_uuid)]
    result = UUIDConvert(from_format="uuid_hex", to_format="hex").transform(
        inputs=[input_values]
    )
    assert result == [str(test_uuid.hex)]


def test_uuid_convert_to_int():
    test_uuid = uuid.uuid4()
    input_values = [str(test_uuid)]
    result = UUIDConvert(from_format="uuid_hex", to_format="int").transform(
        inputs=[input_values]
    )
    assert result == [str(test_uuid.int)]


def test_uuid_convert_to_urn():
    test_uuid = uuid.uuid4()
    input_values = [str(test_uuid)]
    result = UUIDConvert(from_format="uuid_hex", to_format="urn").transform(
        inputs=[input_values]
    )
    assert result == [str(test_uuid.urn)]


def test_uuid_convert_from_int():
    test_uuid = uuid.uuid4()
    input_values = [str(test_uuid.int)]
    result = UUIDConvert(from_format="int", to_format="uuid").transform(
        inputs=[input_values]
    )
    assert result == [str(test_uuid)]


def test_uuid_convert_from_urn():
    test_uuid = uuid.uuid4()
    input_values = [str(test_uuid.urn)]
    result = UUIDConvert(from_format="urn", to_format="uuid").transform(
        inputs=[input_values]
    )
    assert result == [str(test_uuid)]


# Test UUIDVersion


def test_uuid_version():
    input_values = [
        str(uuid.uuid1()),
        str(uuid.uuid3(name="test", namespace=uuid.NAMESPACE_URL)),
        str(uuid.uuid4()),
        str(uuid.uuid5(name="test", namespace=uuid.NAMESPACE_URL)),
        str(uuid6.uuid6()),
        str(uuid6.uuid7()),
        str(uuid6.uuid8()),
        str(uuid6.uuid1_to_uuid6(uuid.uuid1())),
    ]
    result = UUIDVersion().transform(inputs=[input_values])
    assert len(result) == 8
    assert result == [str(i) for i in [1, 3, 4, 5, 6, 7, 8, 6]]
