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
gh ssh-key add ~/.ssh/id_ed25519.pub --title "$(hostnamectl hostname)"

# ghq
sudo pacman -S --needed ghq

# dotfiles
ghq clone https://github.com/toof-jp/dotfiles.git
cd ~/ghq/github.com/toof-jp/dotfiles
make

# pacman package
cd
ghq clone git@github.com:toof-jp/pacman-package-list.git
cd pacman-package-list
./install.sh
cd

# change default shell
chsh -s /usr/bin/zsh

# chsh
set +x
