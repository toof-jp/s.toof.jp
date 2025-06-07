#!/bin/sh
sudo pacman -S --needed git base-devel rustup
rustup default nightly
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si
