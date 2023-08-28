import sys
import typing
from os import makedirs

from loguru import logger
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAnimated

# TODO I will fix this with attrs + cattrs I swear
try:
    from .config import *
except ImportError as e:
    raise ImportError("Cannot import your config. Make sure you have a file called config.py inside of "
                      "stimkysticker/stimkysticker") from e

from .labels.label import StimkyLabelException
from .users import User

client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
client.flood_sleep_threshold = 120
print_log: typing.Dict[int, User] = {}
logger.remove()
logger.add(sys.stdout, level="DEBUG")


@client.on(events.NewMessage(pattern="^/id"))
async def debug_id(ev):
    logger.debug(f"Responding to debug_id event from {ev.peer_id.user_id}")
    await ev.respond(
        f"Hello! Your id is `{ev.peer_id.user_id}` please add it to the ADMIN_ID to give yourself privileges :)"
    )


@client.on(events.NewMessage(pattern="^/info"))
async def info(ev):
    logger.trace(f"Responding to info event from {ev.peer_id.user_id}")
    if ev.peer_id.user_id not in print_log.keys():
        logger.error(f"Printer is currently locked for {ev.peer_id.user_id}")
        await ev.respond(
            "The printer is currently locked for you. Please enter the password!"
        )
        return
    logger.debug(f"Responding to {ev.peer_id.user_id} with user info")
    await ev.respond(f"{print_log[ev.peer_id.user_id].user_info}")


@client.on(events.NewMessage(pattern="^/start"))
async def welcome(ev):
    logger.debug(f"Starting new session with {ev.peer_id.user_id}")
    await ev.respond(
        f"Hello!\nWelcome to {FURSONA_NAME}'s label printer! Send me any sticker or other media to "
        f"print it!"
    )
    if (ev.peer_id.user_id not in print_log.keys()) and PASSWORD:
        logger.error(f"Printer is currently locked for {ev.peer_id.user_id}")
        await ev.respond(
            "The printer is currently locked for you. Please enter the password!"
        )


# This one triggers on a single message with the pin code written
@client.on(events.NewMessage(pattern=PASSWORD, func=lambda e: e.is_private))
async def unlock_printer(ev):
    logger.debug(f"Attempting unlock for {ev.peer_id.user_id}")
    if ev.peer_id.user_id not in print_log.keys():
        print_log.update(
            {
                ev.peer_id.user_id: User.new_user(
                    max_stickers=STICKER_MAX, sticker_cost=STICKER_COST
                )
            }
        )
        if PASSWORD:
            logger.success(f"{ev.peer_id.user_id} has unlocked the printer")
            await ev.respond(
                f"Printer has been unlocked. {print_log[ev.peer_id.user_id].remaining_stickers_str}"
                f" Have fun!"
            )


@client.on(
    events.NewMessage(incoming=True, func=lambda e: e.is_private and e.message.media)
)
async def handler(ev):
    logger.debug(f"New print request from {ev.peer_id.user_id}")
    msg = ev.message
    if ev.peer_id.user_id not in print_log.keys():
        logger.error(f"Printer is currently locked for {ev.peer_id.user_id}")
        await ev.respond(
            "The printer is currently locked for you. Please enter the password!"
        )
        return
    if not print_log[ev.peer_id.user_id].stickers_remaining:
        logger.error(f"{ev.peer_id.user_id} is out of stickers")
        await ev.respond(
            f"Cannot print. {print_log[ev.peer_id.user_id].remaining_stickers_str}"
        )
        return
    # Check if the file is valid
    if msg.photo:
        logger.debug(f"{ev.peer_id.user_id} sent a photo, {msg.photo.id}.jpg")
        recieved_image = Path(CACHE_DIR / f"{msg.photo.id}.jpg")
    elif msg.sticker:
        logger.debug(f"{ev.peer_id.user_id} sent a sticker, {msg.sticker.id}.webp")
        recieved_image = Path(CACHE_DIR / f"{msg.sticker.id}.webp")
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
        await ev.respond("Cannot print this. Try with a (static) sticker or a picture!")
        return

    # Download the file unless it's in the cache!
    if not recieved_image.exists():
        logger.debug(
            f"{ev.peer_id.user_id}'s image {recieved_image} isn't cached, downloading..."
        )
        await client.download_media(msg, file=str(recieved_image))
    try:
        logger.trace("Attempting print...")
        printed = await PRINTER.print(image_file=Path(recieved_image))
    except StimkyPrinterException as e:
        await ev.respond(f"Printer Error: {e.message}")
        logger.error(
            f"Printer Error {e.message} while printing {ev.peer_id.user_id}'s file"
        )
        return
    except StimkyLabelException as e:
        await ev.respond(f"Label Error: {e.message}")
        logger.error(
            f"Label Error {e.message} while printing {ev.peer_id.user_id}'s file"
        )
        return
    except Exception as e:
        await ev.respond(f"Unhandled Error: {e}")
        logger.error(f"Unhandled Error {e} while printing {ev.peer_id.user_id}'s file")
        return

    print_log[ev.peer_id.user_id].use_sticker(image_printed=printed)
    logger.success(f"Printed {printed} for {ev.peer_id.user_id} successfully")
    await ev.respond(
        f"Your sticker has printed!\n{print_log[ev.peer_id.user_id].remaining_stickers_str}"
    )


makedirs(CACHE_DIR, exist_ok=True)
logger.info("Starting client")
client.run_until_disconnected()
