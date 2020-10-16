#!/bin/sh

# because people have no common sense
apt-get install qemu-user-static

bash run.sh -v image A64-OLinuXino buster minimal    A64-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino buster base       A64-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino bionic minimal    A64-OLinuXino-bionic-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A64-OLinuXino bionic base       A64-OLinuXino-bionic-base-$(date +%Y%m%d-%H%M%S).img

bash run.sh -v image A20-OLinuXino buster minimal    A20-OLinuXino-buster-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino buster base       A20-OLinuXino-buster-base-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino bionic minimal    A20-OLinuXino-bionic-minimal-$(date +%Y%m%d-%H%M%S).img
bash run.sh -v image A20-OLinuXino bionic base       A20-OLinuXino-bionic-base-$(date +%Y%m%d-%H%M%S).img
