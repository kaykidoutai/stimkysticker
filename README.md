# stimkysticker
## The better furry sticker printer!

### Based on the [foxo printer_bot](https://git.foxo.me/foxo/printer_bot) 


A sticker printer bot that will print stickers from Telegram to a variety of printers.
Right now we have Brother QL Series support, but the interface is generic enough to add anything. 

# TODO:
- Write README.md usage
- Write README.md installation
- Write a CLI
- Automatic config file generation with `cattrs`
- Option to log loguru to a rolling file
- Save user telemetry to file

## Installation Gotchas
- `brother_ql` accessible via `$PATH`
- User is part of `lp` group (Brother QL) and/or `dialout` (eventual TTL printer)
- Include a `requirements.txt` option for non-poetry users