import typing
from asyncio.streams import StreamWriter
from asyncio.subprocess import PIPE, STDOUT, create_subprocess_shell
from pathlib import Path

from PIL import Image
from serial_asyncio import open_serial_connection

from stimkysticker.labels.brotherdk import BrotherDK

from ..labels.generic import GenericCSNA2Roll
from ..labels.label import Label
from .printer import Printer, StimkyPrinterException


class CSNA2T(Printer):
    uart_dev: Path = Path("/dev/ttyUSB0")
    baud_rate: int = 19200
    name: str = "CSN-A2-T"
    SUPPORTED_LABELS: typing.Tuple[Label] = (GenericCSNA2Roll,)

    CHUNK_HEIGHT = 255
    FIXED_WIDTH = 48
    CHUNK_SIZE = CHUNK_HEIGHT * FIXED_WIDTH
    PRINT_INIT_SEQUENCE = (
        # Print speed and heat
        int(27).to_bytes(length=1, byteorder="little"),
        int(55).to_bytes(length=1, byteorder="little"),
        int(7).to_bytes(length=1, byteorder="little"),  # Default 64 dots = 8*('7'+1)
        int(255).to_bytes(length=1, byteorder="little"),  # Default 80 or 800us
        int(255).to_bytes(length=1, byteorder="little"),  # Default 2 or 20us
        # print density and timeout
        int(18).to_bytes(length=1, byteorder="little"),
        int(35).to_bytes(length=1, byteorder="little"),
        int((15 << 4) | 15).to_bytes(length=1, byteorder="little"),
    )

    _initialized: bool = False

    def __init__(self, using_label: BrotherDK):
        self._label = using_label
        super().__init__(using_label=self._label)

    async def _print(self, image_file: Path) -> Path:
        if not self.uart_dev.exists():
            raise StimkyPrinterException(
                f"Serial UART device {self.uart_dev} for {self.name} does not exist"
            )
        _, writer = await open_serial_connection(
            url=str(self.uart_dev), baudrate=self.baud_rate
        )
        for command in CSNA2T.PRINT_INIT_SEQUENCE:
            writer.write(command)

        formatted_image = self._label.format_image_for_bw_label(image=image_file)
        image_data = await CSNA2T.img_to_csna2_bmp(image_filepath=formatted_image)
        chunked_data = await CSNA2T.split_image_data(image_data=image_data)
        for chunk in chunked_data:
            await self.print_image_chunk(image_chunk=chunk)
        await self.block_serial_write(datas=tuple("\n".encode() for _ in range(3)))
        return formatted_image

    async def block_serial_write(self, datas: typing.Tuple[bytes, ...]):
        """
        For SOME FUCKING REASON awaiting drain() on the async serial connection doesn't ACTUALLY AWAIT.
        The only way you can wait is to wait for the whole connection to close
        :param datas: The data to send
        """
        _, writer = await open_serial_connection(
            url=str(self.uart_dev), baudrate=self.baud_rate
        )
        for data in datas:
            writer.write(data)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def print_image_chunk(self, image_chunk: typing.Tuple[bytes]):
        if len(image_chunk) % CSNA2T.FIXED_WIDTH:
            raise ValueError(
                f"Malformed image chunk. Chunk length must be divisible by {CSNA2T.FIXED_WIDTH}. "
                f"Image chunk length is {len(image_chunk)}, remainder "
                f"{len(image_chunk) % CSNA2T.FIXED_WIDTH}"
            )
        if not image_chunk:
            raise ValueError(f"Malformed image chunk. Data is empty")
        chunk_height = len(image_chunk) / CSNA2T.FIXED_WIDTH
        bitmap_commands = (
            int(18).to_bytes(length=1, byteorder="little"),
            int(86).to_bytes(length=1, byteorder="little"),
            int(chunk_height).to_bytes(length=1, byteorder="little"),
            int(0).to_bytes(length=1, byteorder="little"),
        )
        if chunk_height > CSNA2T.CHUNK_HEIGHT:
            raise ValueError(
                f"Malformed image chunk, too much data. Height must be less than or equal to "
                f"{CSNA2T.CHUNK_HEIGHT}. Height is {len(image_chunk) / CSNA2T.FIXED_WIDTH} "
                f"({len(image_chunk)} total length)"
            )
        await self.block_serial_write(datas=bitmap_commands)
        await self.block_serial_write(datas=image_chunk)

    @staticmethod
    async def img_to_csna2_bmp(image_filepath: Path) -> typing.Tuple[bytes, ...]:
        with Image.open(image_filepath) as image:
            final_data = []
            current_byte = 0
            shifter = 7
            image = image.convert("1")
            pixels = list(image.getdata())
            for pixel in pixels:
                if shifter == -1:
                    final_data.append(
                        int(current_byte).to_bytes(length=1, byteorder="little")
                    )
                    current_byte = 0
                    shifter = 7
                if pixel == 0:
                    current_byte |= 1 << shifter
                shifter -= 1
            final_data.append(int(current_byte).to_bytes(length=1, byteorder="little"))
        return tuple(final_data)

    @staticmethod
    async def split_image_data(
        image_data: typing.Tuple[bytes, ...]
    ) -> typing.Tuple[typing.Tuple[bytes, ...], ...]:
        # Don't split the data if it is too small
        if len(image_data) <= CSNA2T.CHUNK_SIZE:
            return (image_data,)
        # Split the data into chunks of 384 * 255, with the final chunk containing any leftovers
        datas = []
        all_data = []
        for pixel_index in range(len(image_data)):
            if pixel_index % CSNA2T.CHUNK_SIZE == 0 and datas:
                all_data.append(tuple(datas))
                datas = []
            datas.append(image_data[pixel_index])
        if datas:
            all_data.append(datas)
        return tuple(all_data)


async def user_in_dialout() -> bool:
    proc = await create_subprocess_shell("groups", stdout=PIPE, stderr=STDOUT)
    out, err = await proc.communicate()
    return "dialout" in out.decode().split()
