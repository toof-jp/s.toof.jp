#!/bin/sh
set -x

# paru
sudo pacman -S --needed git base-devel rustup
rustup default nightly
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si
cd

# ssh key
ssh-keygen -t ed25519 -C "toof@toof.jp"
sudo pacman -S --needed github-cli
gh auth login
gh ssh-key add ~/.ssh/id_ed25519.pub --title "$(hostname)"
set +x
