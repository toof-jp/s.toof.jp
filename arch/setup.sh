#!/bin/sh
set -x

# paru
sudo pacman -S --needed git base-devel rustup
rustup default nightly
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si
cd

# generate ssh key
ssh-keygen -f ~/.ssh/id_ed25519 -t ed25519 -C "toof@toof.jp"

# upload public key
sudo pacman -S --needed github-cli
gh auth login --git-protocol --skip-ssh-key
gh ssh-key add ~/.ssh/id_ed25519.pub --title "$(hostname)"
set +x
