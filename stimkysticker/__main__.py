import asyncio
import sys
import typing
from importlib.resources import files
from os import makedirs
from pathlib import Path

import click
from loguru import logger
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAnimated

from .config.configfile import DEFAULT_CONFIG_NAME, ConfigFile
from .labels.label import StimkyLabelException
from .printers.brotherql.brotherql import BrotherQl, brother_ql_exists, user_in_lp
from .printers.printer import StimkyPrinterException
from .users import User
from .utils.utils import random_bad_emote, random_happy_emote


async def main_loop(config_file: ConfigFile):
    client = await TelegramClient(
        "bot", int(config_file.api_id), config_file.api_hash
    ).start(bot_token=config_file.bot_token)
    client.flood_sleep_threshold = 120
    print_log: typing.Dict[int, User] = {}
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")

    @client.on(events.NewMessage(pattern="^/id"))
    async def debug_id(ev):
        logger.debug(f"Responding to debug_id event from {ev.peer_id.user_id}")
        await ev.respond(
            f"Hewwo! {random_happy_emote()}\nYour id is `{ev.peer_id.user_id}` please add it to the ADMIN_ID to give"
            f" yourself privileges\n{random_happy_emote()}"
        )

    @client.on(events.NewMessage(pattern="^/info"))
    async def info(ev):
        logger.trace(f"Responding to info event from {ev.peer_id.user_id}")
        if ev.peer_id.user_id not in print_log.keys():
            logger.error(f"Printer is currently locked for {ev.peer_id.user_id}")
            await ev.respond(
                f"The printer is currently locked for you\n{random_bad_emote()}\nPlease enter the password!"
            )
            return
        logger.debug(f"Responding to {ev.peer_id.user_id} with user info")
        await ev.respond(
            f"{random_happy_emote()}\n{print_log[ev.peer_id.user_id].user_info}"
        )

    @client.on(events.NewMessage(pattern="^/start"))
    async def welcome(ev):
        logger.debug(f"Starting new session with {ev.peer_id.user_id}")
        await ev.respond(
            f"Hewwo! {random_happy_emote()}\nWelcome to **{config_file.fursona_name}'s** STIMKY sticker printer!\n"
            f"{random_happy_emote()}\nSend me a sticker or image to print it!\n{random_happy_emote()}"
        )
        if (ev.peer_id.user_id not in print_log.keys()) and config_file.password:
            logger.error(f"Printer is currently locked for {ev.peer_id.user_id}")
            await ev.respond(
                f"The printer is currently locked for you!\n{random_bad_emote()}\nPlease enter the password!"
            )

    # This one triggers on a single message with the pin code written
    @client.on(
        events.NewMessage(pattern=config_file.password, func=lambda e: e.is_private)
    )
    async def unlock_printer(ev):
        logger.debug(f"Attempting unlock for {ev.peer_id.user_id}")
        if ev.peer_id.user_id not in print_log.keys():
            print_log.update(
                {
                    ev.peer_id.user_id: User.new_user(
                        max_stickers=config_file.sticker_max,
                        sticker_cost=config_file.sticker_cost,
                    )
                }
            )
            if config_file.password:
                logger.success(f"{ev.peer_id.user_id} has unlocked the printer")
                await ev.respond(
                    f"Printer is unlocked!!\n{random_happy_emote()}\n{print_log[ev.peer_id.user_id].remaining_stickers_str}\n"
                    f" Have fun! Awoooooooo!\n{random_happy_emote()}"
                )

    @client.on(
        events.NewMessage(
            incoming=True, func=lambda e: e.is_private and e.message.media
        )
    )
    async def handler(ev):
        logger.debug(f"New print request from {ev.peer_id.user_id}")
        msg = ev.message
        if ev.peer_id.user_id not in print_log.keys():
            logger.error(f"Printer is currently locked for {ev.peer_id.user_id}")
            await ev.respond(
                f"The printer is currently locked for you\n{random_bad_emote()}\nPlease enter the password!"
            )
            return
        if not print_log[ev.peer_id.user_id].stickers_remaining:
            logger.error(f"{ev.peer_id.user_id} is out of stickers")
            await ev.respond(
                f"Cannot print\n{random_bad_emote()}\n{print_log[ev.peer_id.user_id].remaining_stickers_str}"
            )
            return
        # Check if the file is valid
        if msg.photo:
            logger.debug(f"{ev.peer_id.user_id} sent a photo, {msg.photo.id}.jpg")
            recieved_image = Path(config_file.cache_dir / f"{msg.photo.id}.jpg")
        elif msg.sticker:
            logger.debug(f"{ev.peer_id.user_id} sent a sticker, {msg.sticker.id}.webp")
            recieved_image = Path(config_file.cache_dir / f"{msg.sticker.id}.webp")
            for att in msg.sticker.attributes:
                if isinstance(att, DocumentAttributeAnimated):
                    logger.debug(f"{ev.peer_id.user_id} sent an animated sticker")
                    recieved_image = None
                    break
        else:
            logger.debug(f"Unable to determine media type sent by {ev.peer_id.user_id}")
            recieved_image = None

        if not recieved_image:
            logger.debug(f"Unable to print file from {ev.peer_id.user_id}")
            await ev.respond(
                f"Cannot print this\n{random_bad_emote()}\nTry with a (static) sticker or a picture! "
                f"{random_happy_emote()}"
            )
            return

        # Download the file unless it's in the cache!
        if not recieved_image.exists():
            await ev.respond(
                f"Downloading your image (can be slow on an RPi {random_happy_emote()} )..."
            )
            logger.debug(
                f"{ev.peer_id.user_id}'s image {recieved_image} isn't cached, downloading..."
            )
            await client.download_media(msg, file=str(recieved_image))
        try:
            await ev.respond(f"Printing! {random_happy_emote()}")
            logger.trace("Attempting print...")
            printed = await config_file.printer.print(image_file=Path(recieved_image))
        except StimkyPrinterException as e:
            await ev.respond(f"{random_bad_emote()} Printer Error: {e.message}")
            logger.error(
                f"Printer Error {e.message} while printing {ev.peer_id.user_id}'s file"
            )
            return
        except StimkyLabelException as e:
            await ev.respond(f"{random_bad_emote()} Label Error: {e.message}")
            logger.error(
                f"Label Error {e.message} while printing {ev.peer_id.user_id}'s file"
            )
            return
        except Exception as e:
            await ev.respond(f"{random_bad_emote()} Unhandled Error: {e}")
            logger.error(
                f"Unhandled Error {e} while printing {ev.peer_id.user_id}'s file"
            )
            return

        print_log[ev.peer_id.user_id].use_sticker(image_printed=printed)
        logger.success(f"Printed {printed} for {ev.peer_id.user_id} successfully")
        await ev.respond(
            f"Your sticker has printed! {random_happy_emote()}\n{print_log[ev.peer_id.user_id].remaining_stickers_str}"
        )

    logger.debug(
        f"Using printer type {config_file.printer.name} and label {config_file.label.name}"
    )
    makedirs(config_file.cache_dir, exist_ok=True)
    logger.info("Starting client")
    await client.run_until_disconnected()


async def _start_daemon(new_config: bool):
    config_file = Path(files("stimkysticker.config").joinpath(DEFAULT_CONFIG_NAME))
    if new_config or not config_file.exists():
        ConfigFile.edit_configfile(config_path=config_file)
        return
    config = ConfigFile.try_load(config_path=config_file)
    if isinstance(config.printer, BrotherQl):
        if not await user_in_lp():
            raise StimkyPrinterException(
                "You are not part of the lp group. Add yourself with "
                "'sudo usermod -aG $USER lp'"
            )
        logger.debug("Ensured that user is part of the lp group")
        if not await brother_ql_exists():
            raise StimkyPrinterException(
                "The brother_ql module is not part of your $PATH. Make sure "
                "'$HOME/.local/bin' is in your path and brother_ql is installed"
            )
        logger.debug("Checked for brother_ql module")
    await main_loop(config_file=config)


@click.command()
@click.option(
    "--new-config",
    default=False,
    is_flag=True,
    help="Recreate your Telegram configuration",
)
def start_daemon(new_config: bool):
    asyncio.run(_start_daemon(new_config=new_config))


if __name__ == "__main__":
    start_daemon()
