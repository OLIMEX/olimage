#!/bin/sh

# because people have no common sense
apt-get install qemu-user-static

bash run.sh -v image A64-OLinuXino buster minimal    A64-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino buster base       A64-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino focal minimal     A64-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino focal base        A64-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img

bash run.sh -v image A20-OLinuXino buster minimal    A20-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino buster base       A20-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino focal minimal     A20-OLinuXino-focal-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino focal base        A20-OLinuXino-focal-base-$(date +%Y%m%d-%H%M%S).img
