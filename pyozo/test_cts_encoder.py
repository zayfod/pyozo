from typing import cast
from .cts_encoder import PacketRequest_MemRead


def test_packet_request_memread_defaults() -> None:
    packet = PacketRequest_MemRead()
    assert isinstance(packet.message_id, int)
    assert packet.message_id == 1
    assert isinstance(packet.address, int)
    assert packet.address == 0
    assert isinstance(packet.length, int)
    assert packet.length == 0


def test_packet_request_memread_custom_values() -> None:
    packet = PacketRequest_MemRead(address=100, length=50)
    assert packet.address == 100
    assert packet.length == 50


def test_packet_request_memread_to_bytes() -> None:
    packet = PacketRequest_MemRead(message_id=2, address=100, length=50)
    assert len(packet) == 8
    byte_data = packet.to_bytes()
    assert isinstance(byte_data, bytes)
    assert len(byte_data) == 8


def test_packet_request_memread_from_bytes() -> None:
    byte_data = b"\x01\x00\x64\x00\x00\x00\x32\x00"
    packet = cast(PacketRequest_MemRead, PacketRequest_MemRead.from_bytes(byte_data))
    assert packet.message_id == 1
    assert packet.address == 100
    assert packet.length == 50
