from .labels.brotherdk import DK2012, DK2205
from .printers.brotherql.ql500 import QL500
from .printers.brotherql.qldummy import QLDummy
from .printers.printer import StimkyPrinterException

# To get an API_ID and API_HASH, you need to sign up to be a Telegram Dev.
# Do it here: https://core.telegram.org/api/obtaining_api_id
API_ID = ""
API_HASH = ""

# Get a bot token from Telegram by creating a bot with @BotFather
BOT_TOKEN = ""

# Limits to prevent abuse
PASSWORD = "12345"  # Set to None if no password required
ADMIN_ID = 1111111111  # Find your own id with the /id command
STICKER_COST = 5 * 60  # Each sticker costs 5 minutes
STICKER_MAX = 5  # Each user can accrue 5 stickers in their bank

# Folder settings
IMAGE_PATH = "/tmp/image.png"
CACHE_DIR = "/tmp/printercache"

FURSONA_NAME = "SomeFur"

# TODO Generate this with cattrs
PRINTER = QLDummy(using_label=DK2012)
