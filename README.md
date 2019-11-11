# Olimex Image builder

## Description

## Directory structure

TODO

## Usage

### User apt-cacher
```shell script
docker-compose up -d
```



### From sources

Generate docker image
```shell script
cd olimage
sudo docker build . -t olimage
```

Run new container
```shell script
docker run -it --privileged  -v $(pwd):/olimage -v /dev:/dev olimage
```

Run script
```shell script
sudo python3 -m olimage --help
```
 
### Running tests
```shell script
python3 -m unittest -v
```

## Developer Manual
### Creating BSP patches

Cleanup the tree:
```shell script
cd output/dl/u-boot/v2019.07
git reset --hard HEAD
git clean -fdx
```

Create new patch:
```shell script
QUILT_PATCHES=/olimage/olimage/packages/u-boot/patches quilt new xxxx-something.patch
quilt add somefile.c
quilt refresh
```
### Generating kernel fragment files

Make sure the kernel tree is clean

```shell script
make mrproper
```

Apply defconfig specified in the board configuration file. For example:

```shell script
make ARCH=arm64 defconfig
```

Make modification with:

```shell script
make ARCH=arm64 menuconfig
```

Generate fragment file:
```shell script
scripts/diffconfig -m
```


python3 -m olimage -v --log=/dev/pts/1 test a64-olinuxino-1G buster minimal