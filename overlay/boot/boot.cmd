# Set default bootargs
{% for key, value in bootargs.items() %}
setenv {{ key }} "{{ value }}"
{% endfor %}

# Print boot source
itest.b *0x10028 == 0x00 && echo "U-boot loaded from SD"
itest.b *0x10028 == 0x02 && echo "U-boot loaded from eMMC or secondary SD"
itest.b *0x10028 == 0x03 && echo "U-boot loaded from SPI"

echo "Boot script loaded from ${devtype}"

# Load uEnv.txt
for prefix in ${boot_prefixes}; do
    echo "Checking for ${prefix}uEnv.txt..."
    if test -e mmc ${mmc_bootdev}:{{ partitions.boot }} ${prefix}uEnv.txt; then
        load mmc ${mmc_bootdev}:1 0x44000000 ${prefix}uEnv.txt
        echo "Loaded environment from ${prefix}uEnv.txt"
        env import -t 0x44000000 ${filesize}
    fi
done

# Get partuuid
if test "${devtype}" = "mmc"; then part uuid mmc ${mmc_bootdev}:{{ partitions.root }} partuuid; fi

# Set bootargs
setenv bootargs "root=PARTUUID=${partuuid} rootwait{% for key, value in bootargs.items() %} {{ key }}={{ '${' }}{{ key }}{{ '}' }}{% endfor %} ${optargs}"

if test -n ${load_legacy} && ${load_legacy}; then
    echo "Loading legacy image format..."

    for prefix in ${boot_prefixes}; do
        if test -e mmc ${mmc_bootdev}:{{ partitions.boot }} ${prefix}Image; then
            load mmc ${mmc_bootdev}:{{ partitions.boot }} ${kernel_addr_r} ${prefix}Image
            load mmc ${mmc_bootdev}:{{ partitions.boot }} ${fdt_addr_r} ${fdtfile}

            booti ${kernel_addr_r} - ${fdt_addr_r}
        fi
    done

fi

# Load kernel.itb
echo "Loading FIT image..."
for prefix in ${boot_prefixes}; do
    if test -e mmc ${mmc_bootdev}:{{ partitions.boot }} ${prefix}{{ fit.file }}; then
        load mmc ${mmc_bootdev}:{{ partitions.boot }} {{ fit.load }} ${prefix}{{ fit.file }}
        if test -n ${boot_config}; then
            bootm {{ fit.load }}#${boot_config}
        else
            bootm {{ fit.load }}
        fi
    fi
done

# Recompile with:
# mkimage -C none -A arm -T script -d /boot/boot.cmd /boot/boot.scr