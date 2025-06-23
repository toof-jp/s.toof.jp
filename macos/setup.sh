#!/bin/sh
set -x

defaults write -g ApplePressAndHoldEnabled -bool false

# generate ssh key
ssh-keygen -f ~/.ssh/id_ed25519 -t ed25519 -C "toof@toof.jp"

# upload public key
gh auth login --git-protocol ssh

ghq clone git@github.com:toof-jp/macos-package-list.git
cd ~/ghq/github.com/toof-jp/macos-package-list
sh brew.sh
sh mas.sh

ghq clone git@github.com:toof-jp/dotfiles.git
cd ~/ghq/github.com/toof-jp/dotfiles
make

ghq clone git@github.com:toof-jp/github-cli-extension-list.git
cd ~/ghq/github.com/toof-jp/github-cli-extension-list
sh install.sh

set +x
