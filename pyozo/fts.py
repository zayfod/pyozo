"""

File trsnsfer service (FTS) module.

"""

from typing import List
from dataclasses import dataclass
import os
import logging
import zlib
import math

from .fts_client import FileTransferServiceClient
from .fts_encoder import (
    MAX_PACKET_SIZE,
    Volume,
    ResponseCode,
    PacketRequest_VolumeSize,
    PacketResponse_VolumeSize,
    PacketRequest_DirectoryListingPath,
    PacketResponse_DirectoryListingPath,
    PacketRequest_FileInfoPath,
    PacketResponse_FileInfoPath,
    PacketRequest_MakeDirectory,
    PacketResponse_MakeDirectory,
    PacketRequest_DeleteFilePath,
    PacketResponse_DeleteFile,
    PacketRequest_DownloadFilePathStart,
    PacketResponse_DownloadFilePathStart,
    PacketRequest_DownloadBlockStart,
    PacketResponse_DownloadBlockStart,
    PacketResponse_DownloadBlockEnd,
    PacketRequest_DownloadEnd,
    PacketRequest_UploadFilePathStart,
    PacketResponse_UploadStart,
    PacketRequest_UploadBlockStart,
    PacketResponse_UploadBlockStart,
    PacketResponse_UploadBlockEnd,
    PacketResponse_UploadEnd,
    raise_for_response_code,
)


__all__ = [
    "DirEntry",
    "VolumeSize",
    "FileTransferService",
]


logger = logging.getLogger("pyozo.fts")


@dataclass
class DirEntry:
    """File-system directory entry."""

    name: str
    is_dir: bool
    size: int
    crc: int


@dataclass
class VolumeSize:
    """File-system volume sizes."""

    size: int
    free: int


class FileTransferService:
    """File Transfer Service (FTS)."""

    BLOCK_SIZE = 500
    """Block size in bytes."""
    BLOCK_TRANSFER_TIMEOUT = 5.0
    """Block transfet timeout in seconds."""

    def __init__(self, client: FileTransferServiceClient) -> None:
        """Constructor."""
        self.client = client
        """File transfer service client instance."""

    async def volume_size(self, volume: Volume) -> VolumeSize:
        """Get volume size request."""
        request = PacketRequest_VolumeSize(volume=volume)
        response = await self.client.request(request)
        if not isinstance(response, PacketResponse_VolumeSize):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_response_code(response.response_code)
        return VolumeSize(response.volume_size, response.free_size)

    async def listdir(self, path: str, provide_crc: bool = False, list_all: bool = False) -> List[DirEntry]:
        """List directory request."""
        flags = 0
        if provide_crc:
            flags |= 0x01
        if list_all:
            flags |= 0x02
        request = PacketRequest_DirectoryListingPath(path=path, flags=flags)
        response = await self.client.request(request)
        res: List[DirEntry] = []
        while True:
            if not isinstance(response, PacketResponse_DirectoryListingPath):
                raise RuntimeError(f"Unexpected response '{response}'.")
            if response.response_code == ResponseCode.LIST_END:
                break
            raise_for_response_code(response.response_code)
            res.append(
                DirEntry(
                    name=response.name,
                    is_dir=response.attributes & 0x01 != 0,
                    size=response.file_size,
                    crc=response.file_crc,
                )
            )
            response = await self.client.wait_response()  # FIXME: Timeout handling.
        return res

    async def download_file(self, path: str) -> bytes:
        """Download file request."""
        data = b""

        # Start file download.
        request = PacketRequest_DownloadFilePathStart(path=path)
        response = await self.client.request(request)
        if not isinstance(response, PacketResponse_DownloadFilePathStart):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_response_code(response.response_code)

        # Write down total file size and CRC.
        file_size = response.file_size
        file_crc = response.file_crc

        offset = 0
        while offset < file_size:
            block_size = min(self.BLOCK_SIZE, file_size - offset)

            self.client.clear_file_data()

            # Request block.
            block_request = PacketRequest_DownloadBlockStart(address=offset, length=block_size)
            try:
                response = await self.client.request(block_request)
            except TimeoutError:
                logger.warning(
                    f"Timeout waiting for PacketResponse_DownloadBlockStart. Retrying block at offset {offset}."
                )
                continue
            if not isinstance(response, PacketResponse_DownloadBlockStart):
                raise RuntimeError(f"Unexpected response '{response}'.")
            raise_for_response_code(response.response_code)

            # Wait for notification that block transfer has been completed.
            try:
                block_end_response = await self.client.wait_response(timeout=self.BLOCK_TRANSFER_TIMEOUT)
            except TimeoutError:
                logger.warning(
                    f"Timeout waiting for PacketResponse_DownloadBlockEnd. Retrying block at offset {offset}."
                )
                continue
            if not isinstance(block_end_response, PacketResponse_DownloadBlockEnd):
                raise RuntimeError(f"Unexpected response '{block_end_response}'.")
            raise_for_response_code(block_end_response.response_code)

            block_data = self.client.file_data

            if block_size != len(block_data):
                logger.warning(f"Block size error. Retrying block at offset {offset}.")
                continue
            block_crc = zlib.crc32(block_data)
            if block_crc != block_end_response.block_crc:
                logger.warning(f"Block CRC error. Retrying block at offset {offset}.")
                continue

            data += block_data
            offset += block_size

        # End file download.
        end_request = PacketRequest_DownloadEnd()
        await self.client.request(end_request, wait_response=False)

        if file_size != len(data):
            raise RuntimeError("File size error.")
        data_crc = zlib.crc32(data)
        if data_crc != file_crc:
            raise RuntimeError("File CRC error.")

        return data

    async def upload_file(self, path: str, data: bytes) -> None:
        """Upload file request."""
        file_size = len(data)
        file_crc = zlib.crc32(data)

        # Start file upload.
        packets_in_block = self.BLOCK_SIZE // MAX_PACKET_SIZE
        request = PacketRequest_UploadFilePathStart(
            path=path, file_size=file_size, file_crc=file_crc, packets_in_block=packets_in_block
        )
        response = await self.client.request(request)
        if not isinstance(response, PacketResponse_UploadStart):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_response_code(response.response_code)

        # Send the file in 500B blocks.
        block_number = response.start_block
        offset = block_number * self.BLOCK_SIZE
        block_crc = 0
        while offset < file_size:
            block_size = min(self.BLOCK_SIZE, file_size - offset)
            block = data[offset : offset + block_size]
            block_crc = zlib.crc32(block, block_crc)
            packets_in_block = math.ceil(block_size / MAX_PACKET_SIZE)

            # Send block.
            block_request = PacketRequest_UploadBlockStart(
                block_number=block_number, packets_in_block=packets_in_block, block_crc=block_crc
            )
            response = await self.client.request(block_request)
            if not isinstance(response, PacketResponse_UploadBlockStart):
                raise RuntimeError(f"Unexpected response '{response}'.")
            raise_for_response_code(response.response_code)

            # Sebd the block in 20B packets.
            block_offset = 0
            while block_offset < block_size:
                packet_size = min(MAX_PACKET_SIZE, block_size - block_offset)
                packet = block[block_offset : block_offset + packet_size]
                await self.client.send_data(packet)
                block_offset += packet_size

            # Wait for notification that block transfer has been completed.
            block_end_response = await self.client.wait_response()  # FIXME: Timeout handling.
            if not isinstance(block_end_response, PacketResponse_UploadBlockEnd):
                raise RuntimeError(f"Unexpected response '{block_end_response}'.")
            raise_for_response_code(block_end_response.response_code)  # TODO: Retry on CRC errors?

            offset += block_size
            block_number += 1

        # Wait for notification that file transfer has been completed.
        upload_end_response = await self.client.wait_response()  # FIXME: Timeout handling.
        if not isinstance(upload_end_response, PacketResponse_UploadEnd):
            raise RuntimeError(f"Unexpected response '{upload_end_response}'.")
        raise_for_response_code(upload_end_response.response_code)

    async def rm(self, path: str) -> None:
        """Remove file-system object request."""
        request = PacketRequest_DeleteFilePath(path=path)
        response = await self.client.request(request)
        if not isinstance(response, PacketResponse_DeleteFile):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_response_code(response.response_code)

    async def mkdir(self, path: str) -> None:
        """Make directory request."""
        request = PacketRequest_MakeDirectory(path=path)
        response = await self.client.request(request)
        if not isinstance(response, PacketResponse_MakeDirectory):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_response_code(response.response_code)

    async def stat(self, path: str) -> DirEntry:
        """File-system object status request."""
        request = PacketRequest_FileInfoPath(path=path)
        response = await self.client.request(request)
        if not isinstance(response, PacketResponse_FileInfoPath):
            raise RuntimeError(f"Unexpected response '{response}'.")
        raise_for_response_code(response.response_code)
        return DirEntry(
            name=os.path.basename(path),
            is_dir=response.flags & 0x01 != 0,
            size=response.file_size,
            crc=response.file_crc,
        )
