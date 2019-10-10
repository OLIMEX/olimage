# Olimex Image builder

## Description
## Usage

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
python3 -m unittest tests/partitions.py
```

## Developer Manual
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
