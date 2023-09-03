import typing
from asyncio.subprocess import PIPE, STDOUT, create_subprocess_shell
from pathlib import Path

from stimkysticker.labels.brotherdk import BrotherDK

from ...labels.label import Label
from ..printer import Printer, StimkyPrinterException


class BrotherQl(Printer):
    usb_dev: Path = Path("/dev/usb/lp0")
    name: str
    SUPPORTED_LABELS: typing.Tuple[Label]

    _err_strs = (
        "status not received",
        "errors occured" "printing potentially not successful",  # [sic]
        "invalid value for",
    )

    def __init__(self, using_label: BrotherDK):
        self._label = using_label
        super().__init__(using_label=self._label)

    async def print(self, image_file: Path) -> Path:
        if not self.usb_dev.exists():
            raise StimkyPrinterException(
                f"USB device {self.usb_dev} for {self.name} does not exist"
            )
        formatted_image = self._label.format_image_for_label(image=image_file)
        cmd = (
            f"brother_ql -m {self.name} -b linux_kernel -p file://{self.usb_dev} print -l {self._label.size_str}"
            f" {formatted_image} -d"
        )
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=STDOUT)
        stdout, stderr = await proc.communicate()
        stdout = stdout.decode("utf-8").splitlines()
        for line in stdout:
            print(line)
        await self.check_errs(stdout=stdout, retcode=proc.returncode)
        return formatted_image

    async def check_errs(self, stdout: typing.List[str], retcode: int):
        await self.check_bad_label(stdout=stdout)
        await self.check_all_other_errs(stdout=stdout, retcode=retcode)

    async def check_bad_label(self, stdout: typing.List[str]):
        for line in stdout:
            if "replace media error".casefold() in line.casefold():
                raise StimkyPrinterException(
                    f"Media error on {self.name} while printing on {self._label.name}. Make "
                    f"sure that {self._label.name} type labels are loaded into the printer "
                    f"and the printer is not out of labels"
                )

    async def check_all_other_errs(self, stdout: typing.List[str], retcode: int):
        errstrs: typing.List[str] = []
        for err in self._err_strs:
            for line in stdout:
                if err.casefold() in line.casefold():
                    errstrs.append(err)
        if errstrs or retcode != 0:
            exception = f"Error on {self.name} while printing onto label {self._label.name}: Got returncode {retcode}"
            newline = "\n"
            if errstrs:
                exception = f"{exception} and errors \n{newline.join(errstrs)}"
                raise StimkyPrinterException(exception)


async def brother_ql_exists() -> bool:
    proc = await create_subprocess_shell("brother_ql", stdout=PIPE, stderr=STDOUT)
    await proc.communicate()
    return proc.returncode == 0


async def user_in_lp() -> bool:
    proc = await create_subprocess_shell("groups", stdout=PIPE, stderr=STDOUT)
    out, err = await proc.communicate()
    return "lp" in out.decode().split()