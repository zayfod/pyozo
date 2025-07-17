from typing import Optional, Tuple
import asyncio
import logging
import zlib

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError

from .protocol_utils import BaseModel
from .cts_encoder import (
    CTRL_CHARACTERISTIC,
    MAX_PACKET_SIZE,
    PacketRequest_MemRead,
    PacketResponse_MemRead,
    PacketRequest_MemWrite,
    PacketResponse_MemWrite,
    PacketRequest_LongRPCExtensionExecute,
    PacketResponse_LongRPCExtensionExecute,
    packet_from_bytes,
    raise_for_ioresult,
    raise_for_call_status,
)
from .virtual_memory import (
    LONG_RPC_EXTENSION_DATA_ADDRESS,
    LONG_RPC_EXTENSION_DATA_SIZE,
)


__all__ = [
    "ControlServiceClient",
]


# Note: 8 is MemWrite request header size.
MAX_REQUEST_BLOCK_SIZE = MAX_PACKET_SIZE - 8
# Note: 5 is MemRead response header size.
MAX_RESPONSE_BLOCK_SIZE = MAX_PACKET_SIZE - 5


logger = logging.getLogger("pyozo.client")


class ControlServiceClient:
    def __init__(self, bleak_client: BleakClient) -> None:
        self.bleak_client = bleak_client
        self.response: Optional[BaseModel] = None
        self.response_event = asyncio.Event()

    async def response_handler(self, packet: BaseModel) -> None:
        logger.debug(f"Got {packet}")
        self.response = packet
        self.response_event.set()

    async def event_handler(self, packet: BaseModel) -> None:
        logger.info(f"Got event {packet}")

    async def notification_handler(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        packet = packet_from_bytes(data)
        if hasattr(packet, "message_id"):
            if packet.message_id < 256:
                await self.response_handler(packet)
            else:
                await self.event_handler(packet)

    async def connect(self) -> None:
        if self.bleak_client.mtu_size < MAX_PACKET_SIZE:
            raise ValueError(f"MTU of {self.bleak_client.mtu_size} too small.")
        await self.bleak_client.start_notify(CTRL_CHARACTERISTIC, self.notification_handler)

    async def disconnect(self) -> None:
        try:
            await self.bleak_client.stop_notify(CTRL_CHARACTERISTIC)
        except BleakError as e:
            if str(e) != "disconnected":
                logger.error(f"Failed to stop notifications. {e}")

    async def wait_response(self, timeout: Optional[float] = None) -> Optional[BaseModel]:
        self.response = None
        self.response_event.clear()
        try:
            await asyncio.wait_for(self.response_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for response.")
            return None  # FIXME: Better handling.
        return self.response

    async def request(self, packet: BaseModel, wait_response: bool = True) -> Optional[BaseModel]:
        data = packet.to_bytes()
        if len(data) <= MAX_PACKET_SIZE:
            await self.bleak_client.write_gatt_char(CTRL_CHARACTERISTIC, data, response=False)
            logger.debug(f"Sent {packet}")
            if wait_response:
                return await self.wait_response()  # FIXME: Timeout handling.
            return None
        else:
            logger.debug(f"Sent Long RPC {packet}")
            return await self.long_rpc_request(data)

    async def mem_read_block(self, address: int, length: int) -> bytes:
        if length > MAX_RESPONSE_BLOCK_SIZE:
            raise ValueError(f"Block size too large ({length}B).")
        request = PacketRequest_MemRead(address=int(address), length=int(length))
        response = await self.request(request)
        if not isinstance(response, PacketResponse_MemRead):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_ioresult(response.result)
        return response.data

    async def mem_read(self, address: int, length: int) -> bytes:
        data = b""
        i = 0
        while i < length:
            block_address = address + i
            block_length = min(MAX_RESPONSE_BLOCK_SIZE, length - i)
            block = await self.mem_read_block(block_address, block_length)
            data += block
            i += block_length
        return data

    async def mem_write_block(self, address: int, data: bytes) -> None:
        length = len(data)
        if length > MAX_REQUEST_BLOCK_SIZE:
            raise ValueError(f"Block size too large ({length}B).")
        request = PacketRequest_MemWrite(address=address, length=length, data=data)
        response = await self.request(request)
        if not isinstance(response, PacketResponse_MemWrite):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_ioresult(response.result)

    async def mem_write(self, address: int, data: bytes) -> None:
        length = len(data)
        i = 0
        while i < length:
            block_address = address + i
            block_length = min(MAX_REQUEST_BLOCK_SIZE, length - i)
            block = data[i : i + block_length]
            await self.mem_write_block(block_address, block)
            i += block_length

    async def long_rpc_execute(self, data_length: int, data_crc: int) -> Tuple[int, int]:
        request = PacketRequest_LongRPCExtensionExecute(data_length=data_length, data_crc=data_crc)
        response = await self.request(request)
        if not isinstance(response, PacketResponse_LongRPCExtensionExecute):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_call_status(response.call_status)
        return response.data_length, response.data_crc

    async def long_rpc_request(self, data: bytes) -> BaseModel:
        packet_len = len(data)
        if packet_len > LONG_RPC_EXTENSION_DATA_SIZE:
            raise ValueError(f"Maximum request length exceeded ({packet_len}).")

        # Transfer the request in blocks.
        await self.mem_write(LONG_RPC_EXTENSION_DATA_ADDRESS, data)

        # Execute.
        packet_crc = zlib.crc32(data)
        data_length, data_crc = await self.long_rpc_execute(packet_len, packet_crc)

        # Retrieve response.
        resp_data = await self.mem_read(LONG_RPC_EXTENSION_DATA_ADDRESS, data_length)
        if data_crc != zlib.crc32(resp_data):
            raise RuntimeError("Long RPC response CRC error.")

        # Deserialize response.
        response = packet_from_bytes(resp_data)
        logger.debug(f"Got long RPC {response}")

        return response
