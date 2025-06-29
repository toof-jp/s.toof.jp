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
gh auth login --git-protocol ssh

# ghq
sudo pacman -S --needed ghq

# dotfiles
ghq clone git@github.com:toof-jp/dotfiles.git
cd ~/ghq/github.com/toof-jp/dotfiles
make
cd

# pacman package
ghq clone git@github.com:toof-jp/pacman-package-list.git
cd ~/ghq/github.com/toof-jp/pacman-package-list
sh install.sh
cd

# docker
sudo usermod -aG docker $USER
newgrp docker

# change default shell
chsh -s /usr/bin/zsh

# docker
sudo systemctl enable --now docker

# tailscale
sudo systemctl enable --now tailscaled
sudo tailscale up

set +x
