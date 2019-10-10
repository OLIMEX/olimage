setenv bootargs "root=/dev/mmcblk0p2 rw console=ttyS0,115200 panic=10 loglevel=7"
setenv bootargs "root=PARTUUID=36c876d5-02 rw console=ttyS0,115200 panic=10 loglevel=7"
setenv bootargs "root=UUID=ab579c7e-7298-4ae4-8c5b-def570449bd6 rw console=ttyS0,115200 panic=10 loglevel=7"


dhcp ${fdt_addr_r} 192.168.0.20:test/sun50i-a64-olinuxino.dtb; dhcp ${kernel_addr_r} 192.168.0.20:test/Image; booti ${kernel_addr_r} - ${fdt_addr_r}
dhcp ${fdt_addr_r} 192.168.0.20:test/sun50i-a64-olinuxino.dtb; dhcp 0x50000000 192.168.0.20:test/Image.gz; unzip 0x50000000 ${kernel_addr_r}; booti ${kernel_addr_r} - ${fdt_addr_r}
dhcp 0x50000000 192.168.0.20:test/kernel.itb; iminfo 0x50000000; bootm 0x50000000

load mmc 0 0x60000000 kernel.itb; iminfo 0x60000000; bootm 0x60000000

load mmc 0 ${fdt_addr_r} sun50i-a64-olinuxino.dtb
load mmc 0 ${kernel_addr_r} Image
booti ${kernel_addr_r} - ${ftd_addr_r}

load mmc 0 ${fdt_addr_r} sun50i-a64-olinuxino.dtb
load mmc 0 0x50000000 Image.gz
unzip 0x50000000 ${kernel_addr_r}
booti ${kernel_addr_r} - ${ftd_addr_r}

#load mmc 0 0x50000000 kernel.itb
imginfo 0x50000000
bootm
#load mmc 0 0x50000000 vmlinuz-5.3.1-1-olimex
#unzip 0x50000000 ${kernel_addr_r}
#booti ${kernel_addr_r} - ${ftd_addr_r}

{% raw %}
{% endraw %}