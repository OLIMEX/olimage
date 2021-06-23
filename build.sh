#!/bin/sh

# because people have no common sense
apt-get install qemu-user-static

# testing images (not recommended, staging repo included)
# a64
bash run.sh -v image A64-OLinuXino buster minimal    A64-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino buster base       A64-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino focal minimal     A64-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino focal base        A64-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

# a20
bash run.sh -v image A20-OLinuXino buster minimal    A20-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino buster base       A20-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino focal minimal     A20-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino focal base        A20-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

# a13
bash run.sh -v image A13-OLinuXino buster minimal    A13-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A13-OLinuXino buster base       A13-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A13-OLinuXino focal minimal     A13-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A13-OLinuXino focal base        A13-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

# a10
bash run.sh -v image A10-OLinuXino buster minimal    A10-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A10-OLinuXino buster base       A10-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A10-OLinuXino focal minimal     A10-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A10-OLinuXino focal base        A10-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

# stm32mp1
bash run.sh -v image STM32MP1-OLinuXino buster minimal    STM32MP1-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image STM32MP1-OLinuXino focal minimal     STM32MP1-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image STM32MP1-OLinuXino-SOM buster minimal    STM32MP1-OLinuXino-SOM-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image STM32MP1-OLinuXino-SOM focal minimal     STM32MP1-OLinuXino-SOM-focal-minimal-$(date +%Y%m%d-%H%M%S).img

# release images
# a64
ARGS=-r bash run.sh -v image A64-OLinuXino buster minimal    A64-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A64-OLinuXino buster base       A64-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A64-OLinuXino focal minimal     A64-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A64-OLinuXino focal base        A64-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

# a20
ARGS=-r bash run.sh -v image A20-OLinuXino buster minimal    A20-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A20-OLinuXino buster base       A20-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A20-OLinuXino focal minimal     A20-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A20-OLinuXino focal base        A20-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

# a13
ARGS=-r bash run.sh -v image A13-OLinuXino buster minimal    A13-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A13-OLinuXino buster base       A13-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A13-OLinuXino focal minimal     A13-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A13-OLinuXino focal base        A13-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

# a10
ARGS=-r bash run.sh -v image A10-OLinuXino buster minimal    A10-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A10-OLinuXino buster base       A10-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A10-OLinuXino focal minimal     A10-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image A10-OLinuXino focal base        A10-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

# stm32mp1
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino buster minimal    STM32MP1-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino focal minimal     STM32MP1-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img

ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-SOM buster minimal    STM32MP1-OLinuXino-SOM-buster-minimal-$(date +%Y%m%d-%H%M%S).img
ARGS=-r bash run.sh -v image STM32MP1-OLinuXino-SOM focal minimal     STM32MP1-OLinuXino-SOM-focal-minimal-$(date +%Y%m%d-%H%M%S).img
