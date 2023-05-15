#!/bin/sh

# qemu-user-static != 5.2 may have issues when building bullseye arm64 images
# recommended host OS to build: debian buster amd64 with qemu-user-static from buster-backports
apt-get install qemu-user-static

# testing images (not recommended, staging repo included)
# a64
bash run.sh -v image A64-OLinuXino bullseye minimal    A64-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino bullseye base       A64-OLinuXino-bullseye-base-$(date +%Y%m%d-%H%M%S).img

# a20
bash run.sh -v image A20-OLinuXino bullseye minimal    A20-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino bullseye base       A20-OLinuXino-bullseye-base-$(date +%Y%m%d-%H%M%S).img

# a13
bash run.sh -v image A13-OLinuXino bullseye minimal    A13-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A13-OLinuXino bullseye base       A13-OLinuXino-bullseye-base-$(date +%Y%m%d-%H%M%S).img

# a10
bash run.sh -v image A10-OLinuXino bullseye minimal    A10-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A10-OLinuXino bullseye base       A10-OLinuXino-bullseye-base-$(date +%Y%m%d-%H%M%S).img

# stm32mp1
bash run.sh -v image STM32MP1-OLinuXino-LIME bullseye minimal     STM32MP1-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image STM32MP1-OLinuXino-SOM bullseye minimal      STM32MP1-OLinuXino-SOM-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image STM32MP1-OLinuXino-SOM-BASE bullseye minimal STM32MP1-OLinuXino-SOM-BASE-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img

# release images
# a64
ARGS=-r bash run.sh -v image A64-OLinuXino bullseye minimal    A64-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A64-OLinuXino bullseye base       A64-OLinuXino-bullseye-base-$(date +%Y%m%d-%H%M%S).img

# a20
ARGS=-r bash run.sh -v image A20-OLinuXino bullseye minimal    A20-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A20-OLinuXino bullseye base       A20-OLinuXino-bullseye-base-$(date +%Y%m%d-%H%M%S).img

# a13
ARGS=-r bash run.sh -v image A13-OLinuXino bullseye minimal    A13-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A13-OLinuXino bullseye base       A13-OLinuXino-bullseye-base-$(date +%Y%m%d-%H%M%S).img

# a10
ARGS=-r bash run.sh -v image A10-OLinuXino bullseye minimal    A10-OLinuXino-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A10-OLinuXino bullseye base       A10-OLinuXino-bullseye-base-$(date +%Y%m%d-%H%M%S).img

# stm32mp1-lime
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-LIME bullseye minimal     STM32MP1-OLinuXino-LIME-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-LIME bullseye base        STM32MP1-OLinuXino-LIME-bullseye-base-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-SOM bullseye minimal      STM32MP1-OLinuXino-SOM-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-SOM-BASE bullseye minimal STM32MP1-OLinuXino-SOM-BASE-bullseye-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-SOM-BASE bullseye base    STM32MP1-OLinuXino-SOM-BASE-bullseye-base-$(date +%Y%m%d-%H%M%S).img
