#!/usr/bin/env bash

gpg --list-keys --keyid-format LONG
key_id=$(gpg --list-keys --keyid-format LONG | grep "^pub " | sed "s/.*\/\([^ ]*\).*/\1/")

echo "Exporting key: ${key_id}"
gpg2 --armor --export ${key_id} | tee /data/keys/olimage.gpg
chown 1000:1000 /data/keys/olimage.gpg

echo "Checking repository..."
reprepro check

# Keep the container alive
tail -f /dev/null