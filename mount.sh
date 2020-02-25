#!/bin/bash

_path=$1

[[ ! -d ${_path} ]] && echo "Target path not found!" >&2

set -x

mount -t proc /proc "${_path}"/proc
mount --bind /sys "${_path}/sys"
mount --bind /dev "${_path}/dev"
mount --bind /dev/pts "${_path}/dev/pts"
mkdir "${_path}/run/dbus"
mount --bind /run/dbus "${_path}/run/dbus"

chroot "${_path}"

umount "${_path}/run/dbus"
umount "${_path}/dev/pts"
umount "${_path}/dev"
umount "${_path}/sys"
umount "${_path}/proc"
