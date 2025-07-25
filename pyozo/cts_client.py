"""

Control service client module.

"""

from typing import Dict, Optional, Tuple, Callable, Awaitable, TypeAlias, cast
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
    message_id,
)
from .virtual_memory import (
    LONG_RPC_EXTENSION_DATA_ADDRESS,
    LONG_RPC_EXTENSION_DATA_SIZE,
)


__all__ = [
    "EventHandler",
    "ControlServiceClient",
]


# Note: 8 is MemWrite request header size.
MAX_REQUEST_BLOCK_SIZE = MAX_PACKET_SIZE - 8
"""Maximum request block size in bytes."""
# Note: 5 is MemRead response header size.
MAX_RESPONSE_BLOCK_SIZE = MAX_PACKET_SIZE - 5
"""Maximum response block size in bytes."""


EventHandler: TypeAlias = Callable[[BaseModel], Awaitable[None]]


logger = logging.getLogger("pyozo.client")


class ControlServiceClient:
    """Control Service client class."""

    def __init__(self, bleak_client: BleakClient) -> None:
        """Constructor."""
        self.bleak_client = bleak_client
        """Bleak client instance."""
        self.pending_requests_lock = asyncio.Lock()
        """Lock to protect access to pending_requests."""
        self.pending_requests: Dict[Tuple[int, int], asyncio.Future[BaseModel]] = {}
        """Map of (message_id,request_id)->Future for pending requests."""
        self.event_handler: Optional[EventHandler] = None

    async def response_handler(self, packet: BaseModel) -> None:
        """Response handler method."""
        logger.debug(f"Got {packet}")
        message_id = packet.message_id if hasattr(packet, "message_id") else -1
        request_id = packet.request_id if hasattr(packet, "request_id") else -1
        async with self.pending_requests_lock:
            future = self.pending_requests.pop((message_id, request_id), None)
        if future:
            future.set_result(packet)
        else:
            logger.warning(f"Got response {packet} without pending request.")

    async def _event_handler(self, packet: BaseModel) -> None:
        logger.debug(f"Got event {packet}")
        message_id = packet.message_id if hasattr(packet, "message_id") else -1
        request_id = packet.request_id if hasattr(packet, "request_id") else -1
        async with self.pending_requests_lock:
            future = self.pending_requests.pop((message_id, request_id), None)
        if future:
            future.set_result(packet)
        else:
            # FIXME: Spurious event handling.
            if self.event_handler is not None:
                await self.event_handler(packet)

    async def notification_handler(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        """Bluetooth characteristic notification handler method."""
        packet = packet_from_bytes(data)
        if hasattr(packet, "message_id"):
            if packet.message_id < 256:
                await self.response_handler(packet)
            else:
                await self._event_handler(packet)

    async def connect(self) -> None:
        """Connect to the control Bluetooth service."""
        if self.bleak_client.mtu_size < MAX_PACKET_SIZE:
            raise ValueError(f"MTU of {self.bleak_client.mtu_size} too small.")
        await self.bleak_client.start_notify(CTRL_CHARACTERISTIC, self.notification_handler)

    async def disconnect(self) -> None:
        """Disconnect from the control Bluetooth service."""
        try:
            await self.bleak_client.stop_notify(CTRL_CHARACTERISTIC)
        except BleakError as e:
            if str(e) != "disconnected":
                logger.error(f"Failed to stop notifications. {e}")
        await self._cancel_pending_requests()

    async def _cancel_pending_requests(self) -> None:
        async with self.pending_requests_lock:
            for future in self.pending_requests.values():
                if not future.done():
                    future.set_exception(asyncio.CancelledError())
            self.pending_requests.clear()

    async def request(
        self, packet: BaseModel, response_message_id: int, request_id: int = -1, timeout: float = 3.0
    ) -> Optional[BaseModel]:
        """Send a request packet to the control service."""
        data = packet.to_bytes()
        if len(data) <= MAX_PACKET_SIZE:
            if timeout >= 0.0:
                future = asyncio.get_event_loop().create_future()
                async with self.pending_requests_lock:
                    self.pending_requests[(response_message_id, request_id)] = future
            await self.bleak_client.write_gatt_char(CTRL_CHARACTERISTIC, data, response=False)
            logger.debug(f"Sent {packet}")
            if timeout >= 0.0:
                try:
                    return await asyncio.wait_for(future, timeout=timeout)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout waiting for ({response_message_id}, {request_id}) response.")
                    async with self.pending_requests_lock:
                        self.pending_requests.pop((response_message_id, request_id), None)
                    raise
            return None
        else:
            logger.debug(f"Sent Long RPC {packet}")
            return await self.long_rpc_request(data)

    async def mem_read_block(self, address: int, length: int) -> bytes:
        """Send a memory read block request."""
        if length > MAX_RESPONSE_BLOCK_SIZE:
            raise ValueError(f"Block size too large ({length}B).")
        request = PacketRequest_MemRead(address=int(address), length=int(length))
        response = await self.request(request, message_id(PacketResponse_MemRead))
        response = cast(PacketResponse_MemRead, response)
        raise_for_ioresult(response.result)
        return response.data

    async def mem_read(self, address: int, length: int) -> bytes:
        """Send a memory read request."""
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
        """Send a memory write block request."""
        length = len(data)
        if length > MAX_REQUEST_BLOCK_SIZE:
            raise ValueError(f"Block size too large ({length}B).")
        request = PacketRequest_MemWrite(address=address, length=length, data=data)
        response = await self.request(request, message_id(PacketResponse_MemWrite))
        response = cast(PacketResponse_MemWrite, response)
        raise_for_ioresult(response.result)

    async def mem_write(self, address: int, data: bytes) -> None:
        """Send a memory write request."""
        length = len(data)
        i = 0
        while i < length:
            block_address = address + i
            block_length = min(MAX_REQUEST_BLOCK_SIZE, length - i)
            block = data[i : i + block_length]
            await self.mem_write_block(block_address, block)
            i += block_length

    async def long_rpc_execute(self, data_length: int, data_crc: int) -> Tuple[int, int]:
        """Make a long RPC extension execute request."""
        request = PacketRequest_LongRPCExtensionExecute(data_length=data_length, data_crc=data_crc)
        response = await self.request(request, message_id(PacketResponse_LongRPCExtensionExecute))
        response = cast(PacketResponse_LongRPCExtensionExecute, response)
        raise_for_call_status(response.call_status)
        return response.data_length, response.data_crc

    async def long_rpc_request(self, data: bytes) -> BaseModel:
        """Send a long RPC extension request."""
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

    async def wait_for_event(self, event_message_id: int, request_id: int, timeout: Optional[float]) -> BaseModel:
        """Wait for an event in response to a specific request.."""
        future = asyncio.get_event_loop().create_future()
        async with self.pending_requests_lock:
            self.pending_requests[(event_message_id, request_id)] = future
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for ({event_message_id, request_id}) event.")
            async with self.pending_requests_lock:
                self.pending_requests.pop((event_message_id, request_id), None)
            raise
