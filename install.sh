#!/bin/bash
# Create a Python virtual environment (venv).
python -m venv venv
source venv/bin/activate
# Install python dependencies:
pip install -r requirements.txt
# Install the console player mpv:
install_mpv() {
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y mpv
    elif command -v yum &> /dev/null; then
        sudo yum install -y mpv
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y mpv
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y mpv
    elif command -v pacman &> /dev/null; then
        sudo pacman -S mpv
    else
        echo "Unsupported package manager. Please install mpv manually."
        exit 1
    fi
}
install_mpv
