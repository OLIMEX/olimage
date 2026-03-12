#!/bin/sh

# qemu-user-static != 5.2 may have issues when building bookworm arm64 images
# recommended host OS to build: debian buster amd64 with qemu-user-static from buster-backports
apt-get install qemu-user-static

# testing images (not recommended, staging repo included)
# a64
bash run.sh -v image A64-OLinuXino bookworm minimal    A64-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino bookworm base       A64-OLinuXino-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# a20
bash run.sh -v image A20-OLinuXino bookworm minimal    A20-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino bookworm base       A20-OLinuXino-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# a13
bash run.sh -v image A13-OLinuXino bookworm minimal    A13-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A13-OLinuXino bookworm base       A13-OLinuXino-bookworm-base-$(date +%Y%m%d-%H%M%S).img

bash run.sh -v image A13-SOM bookworm minimal          A13-SOM-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A13-SOM bookworm base             A13-SOM-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# a10
bash run.sh -v image A10-OLinuXino bookworm minimal    A10-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A10-OLinuXino bookworm base       A10-OLinuXino-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# stm32mp1
bash run.sh -v image STM32MP1-OLinuXino-LIME bookworm minimal     STM32MP1-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image STM32MP1-OLinuXino-SOM bookworm minimal      STM32MP1-OLinuXino-SOM-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image STM32MP1-OLinuXino-SOM-BASE bookworm minimal STM32MP1-OLinuXino-SOM-BASE-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image STM32MP1-OLinuXino-SOM-BASE bookworm base    STM32MP1-OLinuXino-SOM-BASE-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# release images
# a64
ARGS=-r bash run.sh -v image A64-OLinuXino bookworm minimal    A64-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A64-OLinuXino bookworm base       A64-OLinuXino-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# a20
ARGS=-r bash run.sh -v image A20-OLinuXino bookworm minimal    A20-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A20-OLinuXino bookworm base       A20-OLinuXino-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# a13
ARGS=-r bash run.sh -v image A13-OLinuXino bookworm minimal    A13-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A13-OLinuXino bookworm base       A13-OLinuXino-bookworm-base-$(date +%Y%m%d-%H%M%S).img

ARGS=-r bash run.sh -v image A13-SOM bookworm minimal          A13-SOM-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A13-SOM bookworm base             A13-SOM-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# a10
ARGS=-r bash run.sh -v image A10-OLinuXino bookworm minimal    A10-OLinuXino-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A10-OLinuXino bookworm base       A10-OLinuXino-bookworm-base-$(date +%Y%m%d-%H%M%S).img

# stm32mp1-lime
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-LIME bookworm minimal     STM32MP1-OLinuXino-LIME-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-LIME bookworm base        STM32MP1-OLinuXino-LIME-bookworm-base-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-SOM bookworm minimal      STM32MP1-OLinuXino-SOM-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-SOM-BASE bookworm minimal STM32MP1-OLinuXino-SOM-BASE-bookworm-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-SOM-BASE bookworm base    STM32MP1-OLinuXino-SOM-BASE-bookworm-base-$(date +%Y%m%d-%H%M%S).img
