from __future__ import annotations

import json
import typing
from pathlib import Path

from attr import dataclass

from stimkysticker.converters import (
    structure_label,
    structure_printer,
    unstructure_label,
    unstructure_printer,
)
from stimkysticker.labels.label import Label
from stimkysticker.printers import PRINTER_DICT
from stimkysticker.printers.printer import Printer

DEFAULT_CONFIG_NAME = Path("stimky_config.json")


@dataclass
class ConfigFile:
    api_id: str
    api_hash: str

    bot_token: str

    password: str
    admin_id: int
    fursona_name: str

    printer: Printer
    label: Label

    max_aspect_ratio: float = 1.5
    sticker_cost: int = 5 * 60
    sticker_max: int = 5

    image_path: Path = Path("/tmp/image.png")
    cache_dir: Path = Path("/tmp/printercache")

    gamma_correction: float = 1.8
    background_color: str = "white"

    @staticmethod
    def try_load(config_path: Path) -> ConfigFile:
        if not config_path.exists():
            print("Configfile not found, initializing")
            config = InteractiveConfigBuilder.interactive_config_builder(
                default_config=None
            )
            config.to_json(configfile=config_path)
        else:
            try:
                config = ConfigFile.from_json(configfile=config_path)
            except Exception as e:
                print(
                    f"There is an issue with your config file, {e}. Please re-initialize"
                )
                config = InteractiveConfigBuilder.interactive_config_builder(
                    default_config=None
                )
                config.to_json(configfile=config_path)
        return config

    @staticmethod
    def edit_configfile(config_path: Path) -> None:
        try:
            config = ConfigFile.from_json(configfile=config_path)
            config = InteractiveConfigBuilder.interactive_config_builder(
                default_config=config
            )
            config.to_json(configfile=config_path)
        except Exception as e:
            print(f"There is an issue with your config file, {e}. Please re-initialize")
            config = InteractiveConfigBuilder.interactive_config_builder(
                default_config=None
            )
            config.to_json(configfile=config_path)

    def to_json(self, configfile: Path):
        data = {
            "api_id": f"{self.api_id}",
            "api_hash": f"{self.api_hash}",
            "bot_token": f"{self.bot_token}",
            "password": f"{self.password}",
            "max_aspect_ratio": f"{self.max_aspect_ratio}",
            "admin_id": f"{self.admin_id}",
            "sticker_cost": f"{self.sticker_cost}",
            "sticker_max": f"{self.sticker_max}",
            "fursona_name": f"{self.fursona_name}",
            "image_path": f"{self.image_path}",
            "cache_dir": f"{self.cache_dir}",
            "gamma_correction": f"{self.gamma_correction}",
            "background_color": f"{self.background_color}",
            "label": f"{structure_label(label=self.label)}",
            "printer": f"{structure_printer(printer=self.printer)}",
        }
        configfile.write_text(json.dumps(data))

    @classmethod
    def from_json(cls, configfile: Path) -> ConfigFile:
        configdata = json.loads(configfile.read_text(encoding="utf-8"))
        label_str = raw = cls._try_get(configdata=configdata, key="label")
        label = unstructure_label(raw=label_str)
        printer = unstructure_printer(
            printer=cls._try_get(configdata=configdata, key="printer"), label=label_str
        )

        return ConfigFile(
            api_id=cls._try_get(configdata=configdata, key="api_id"),
            api_hash=cls._try_get(configdata=configdata, key="api_hash"),
            bot_token=cls._try_get(configdata=configdata, key="bot_token"),
            password=cls._try_get(configdata=configdata, key="password"),
            max_aspect_ratio=float(
                cls._try_get(configdata=configdata, key="max_aspect_ratio")
            ),
            admin_id=int(cls._try_get(configdata=configdata, key="admin_id")),
            sticker_cost=int(cls._try_get(configdata=configdata, key="sticker_cost")),
            sticker_max=int(cls._try_get(configdata=configdata, key="sticker_max")),
            fursona_name=cls._try_get(configdata=configdata, key="fursona_name"),
            image_path=Path(cls._try_get(configdata=configdata, key="image_path")),
            cache_dir=Path(cls._try_get(configdata=configdata, key="cache_dir")),
            gamma_correction=float(
                cls._try_get(configdata=configdata, key="gamma_correction")
            ),
            background_color=cls._try_get(
                configdata=configdata, key="background_color"
            ),
            label=label,
            printer=printer,
        )

    @classmethod
    def _try_get(cls, configdata: dict, key: str) -> str:
        if configdata.get(key) is None:
            raise ValueError(f"{key} is not present in config file")
        return configdata[key]


class InteractiveConfigBuilder:
    @staticmethod
    def get_type(datatype: type, data: str):
        try:
            return datatype(data)
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def keep_prompting(
        datatype: type,
        prompt: str,
        default: typing.Optional[str],
        choices: typing.Tuple[str] = (),
    ):
        data = None
        while data is None:
            choices_txt = f" [Choices: {', '.join(choices)}]" if choices else ""
            default_txt = f" [Default: {default}]" if default else ""
            inputdata = input(f"{prompt}{default_txt}{choices_txt}")
            if not inputdata and default:
                return default
            data = InteractiveConfigBuilder.get_type(datatype=datatype, data=inputdata)
            if data is None:
                print(f"{inputdata} is not a valid {datatype}")
            else:
                if choices:
                    if data in choices:
                        return data
                    else:
                        print(
                            f"{data} is not a valid choice. Please choose {', '.join(choices)}"
                        )
                        data = None
                else:
                    return data

    @staticmethod
    def interactive_config_builder(
        default_config: typing.Optional[ConfigFile] = None,
    ) -> ConfigFile:
        default_api_id = default_config.api_id if default_config is not None else None
        default_api_hash = (
            default_config.api_hash if default_config is not None else None
        )
        default_bot_token = (
            default_config.bot_token if default_config is not None else None
        )
        default_password = (
            default_config.password if default_config is not None else None
        )
        default_admin_id = (
            str(default_config.admin_id) if default_config is not None else None
        )
        default_fursona_name = (
            default_config.fursona_name if default_config is not None else None
        )
        default_printer = (
            default_config.printer.name.casefold()
            if default_config is not None
            else None
        )
        default_label = (
            default_config.label.name.casefold() if default_config is not None else None
        )
        api_id = (
            InteractiveConfigBuilder.keep_prompting(
                datatype=str,
                prompt="What is your Telegram API ID?",
                default=default_api_id,
            )
            .replace(" ", "")
            .rstrip()
        )
        api_hash = (
            InteractiveConfigBuilder.keep_prompting(
                datatype=str,
                prompt="What is your Telegram API hash?",
                default=default_api_hash,
            )
            .replace(" ", "")
            .rstrip()
        )
        bot_token = (
            InteractiveConfigBuilder.keep_prompting(
                datatype=str,
                prompt="What is your Telegram Bot Token?",
                default=default_bot_token,
            )
            .replace(" ", "")
            .rstrip()
        )
        password = (
            InteractiveConfigBuilder.keep_prompting(
                datatype=str,
                prompt="What do you want to set the sticker password to?",
                default=default_password,
            )
            .replace(" ", "")
            .rstrip()
        )
        admin_id = InteractiveConfigBuilder.keep_prompting(
            datatype=int, prompt="What is your Telegram ID?", default=default_admin_id
        )
        fursona_name = (
            InteractiveConfigBuilder.keep_prompting(
                datatype=str,
                prompt="What is your fursona name? UwU",
                default=default_fursona_name,
            )
            .replace(" ", "")
            .rstrip()
        )
        printer = InteractiveConfigBuilder.keep_prompting(
            datatype=str,
            prompt="What printer are you using?",
            default=default_printer,
            choices=tuple(PRINTER_DICT.keys()),
        )
        label = InteractiveConfigBuilder.keep_prompting(
            datatype=str,
            prompt="What label are you using?",
            default=default_label,
            choices=tuple(
                label.name.casefold()
                for label in PRINTER_DICT[printer].SUPPORTED_LABELS
            ),
        )
        printer = unstructure_printer(printer=printer, label=label)
        label = unstructure_label(raw=label)
        return ConfigFile(
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            password=password,
            admin_id=admin_id,
            fursona_name=fursona_name,
            printer=printer,
            label=label,
        )
