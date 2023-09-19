#!/bin/sh

echo "This script will do the following"
echo "- Install all required dependencies"
echo "- Add the current user to the lp group so they can print"
echo "- Add \$HOME/.local/bin to \$PATH so you can execute brother-ql"
echo "- Walk you through creating a config"
sleep 1


if ($(which poetry > /dev/null)) ; then
    echo "Installing all deps with poetry"
    poetry install
else
    echo "Installing all deps with requirements.txt to system python"
    dpkg -s python3-pip > /dev/null || sudo apt install -y python3-pip
    python3 -m pip install -r requirements.txt
fi

echo "Adding user to lp group"
current_user=$(whoami)
sudo usermod -aG lp $current_user

if ($(brother_ql > /dev/null)) ; then
    echo "Warning: cannot access brother_ql! You may need to add \$HOME/.local/bin to your \$PATH"
fi

echo "Creating a new stimkysticker config"
python3 -m stimkysticker --new-config

echo "Done! If you need to edit your config file, run "
echo "python3 -m stimkysticker --new-config"
echo "Don't run this script again!"
echo "Make sure to restart your computer for all changes to take affect"