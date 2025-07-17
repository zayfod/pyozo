from typing import List, Optional
import asyncio
import logging

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError

from .protocol_utils import BaseModel
from .fts_encoder import (
    FTS_DATA_CHARACTERISTIC,
    FTS_CMD_CHARACTERISTIC,
    MAX_PACKET_SIZE,
    Packet_Fragment,
    Packet_Fragment_Confirmation,
    Packet_UnexpectedPacket,
    packet_from_bytes,
)


__all__ = [
    "FileTransferServiceClient",
]


# Note: 2 is Packet_Fragment header size.
MAX_FRAGMENT_SIZE = MAX_PACKET_SIZE - 2


logger = logging.getLogger("pyozo.fts_client")


class FileTransferServiceClient:
    RESPONSE_TIMEOUT = 2.0

    def __init__(self, bleak_client: BleakClient) -> None:
        self.bleak_client = bleak_client
        self.fragments: List[Packet_Fragment] = []
        self.file_data = b""
        self.response: List[Optional[BaseModel]] = []
        self.response_event = asyncio.Event()

    async def response_handler(self, packet: BaseModel) -> None:
        logger.debug(f"Got {packet}")
        self.response.append(packet)
        self.response_event.set()

    async def notification_handler(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        packet = packet_from_bytes(data)
        if isinstance(packet, Packet_Fragment):
            # Fragmented packet
            self.fragments.append(packet)
            if packet.index & 0x80:  # Last fragment
                # Last fragment
                full_data = b"".join(fragment.data for fragment in self.fragments)
                self.fragments.clear()
                packet = packet_from_bytes(full_data)
                await self.response_handler(packet)
        else:
            await self.response_handler(packet)

    async def data_notification_handler(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        logger.debug(f"Got {len(data)}B data.")
        self.file_data += data

    def clear_file_data(self) -> None:
        self.file_data = b""

    async def connect(self) -> None:
        if self.bleak_client.mtu_size < MAX_PACKET_SIZE:
            raise ValueError(f"MTU of {self.bleak_client.mtu_size} too small.")
        await self.bleak_client.start_notify(FTS_DATA_CHARACTERISTIC, self.data_notification_handler)
        await self.bleak_client.start_notify(FTS_CMD_CHARACTERISTIC, self.notification_handler)

    async def disconnect(self) -> None:
        try:
            await self.bleak_client.stop_notify(FTS_CMD_CHARACTERISTIC)
            await self.bleak_client.stop_notify(FTS_DATA_CHARACTERISTIC)
        except BleakError as e:
            if str(e) != "disconnected":
                logger.error(f"Failed to stop notifications. {e}")

    async def wait_response(self, timeout: Optional[float] = RESPONSE_TIMEOUT) -> Optional[BaseModel]:
        if not self.response:
            self.response_event.clear()
            try:
                await asyncio.wait_for(self.response_event.wait(), timeout=timeout)
            except asyncio.TimeoutError as e:
                logger.warning("Timeout waiting for response.")
                raise TimeoutError("Timeout waiting for response.") from e
        response = self.response.pop(0)
        if isinstance(response, Packet_UnexpectedPacket):
            raise RuntimeError("File transfer communication out of sync.")
        return response

    async def request(self, packet: BaseModel, wait_response: bool = True) -> Optional[BaseModel]:
        data = packet.to_bytes()
        if len(data) <= MAX_PACKET_SIZE:
            await self.bleak_client.write_gatt_char(FTS_CMD_CHARACTERISTIC, data, response=False)
            logger.debug(f"Sent {packet}")
        else:
            logger.debug(f"Sent fragmented {packet}")
            await self.request_fragmented(data)
        if wait_response:
            return await self.wait_response()
        return None

    async def request_fragmented(self, data: bytes) -> None:
        length = len(data)
        if length > 128 * MAX_FRAGMENT_SIZE:
            raise ValueError(f"Request too large ({length}B).")
        fragment_count = length // MAX_FRAGMENT_SIZE + 1
        fragment_index = 0
        i = 0
        while i < length:
            fragment_length = min(MAX_FRAGMENT_SIZE, length - i)
            fragment = data[i : i + fragment_length]
            if fragment_index >= fragment_count - 1:
                fragment_index |= 0x80  # Last fragment.
            request = Packet_Fragment(index=fragment_index, data=fragment)
            response = await self.request(request)
            if not isinstance(response, Packet_Fragment_Confirmation):
                raise RuntimeError(f"Unexpected response '{response}'.")
            i += fragment_length
            fragment_index += 1

    async def send_data(self, data: bytes) -> None:
        await self.bleak_client.write_gatt_char(FTS_DATA_CHARACTERISTIC, data, response=False)
        logger.debug(f"Sent {len(data)}B data.")
