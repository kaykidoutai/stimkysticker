# stimkysticker
## The better furry sticker printer!

### Based on the [foxo printer_bot](https://git.foxo.me/foxo/printer_bot) 


A sticker printer bot that will print stickers from Telegram to a variety of printers.
Right now we have Brother QL Series support, but the interface is generic enough to add anything. 

## Installation
1) Add yourself to the `lp` group so you can talk to the label printer
```commandline
sudo usermod -aG $USER lp
```
2) Install package
```commandline
poetry install  # If using poetry
python3 -m pip install -r requirements.txt  # If using pip
```
3) Add `$HOME/.local/bin` to your `$PATH` so you can call `brother_ql`
4) Reboot
```commandline
sudo reboot
```

## Usage
### Poetry
```text
Usage: python -m stimkysticker [OPTIONS]

Options:
  --new-config  Recreate your Telegram configuration
  --help        Show this message and exit.
```
```commandline
poetry shell  # If using poetry
python3 -m stimkysticker  # Starts the daemon
```

# TODO:
- Option to log loguru to a rolling file
- Save user telemetry to file

