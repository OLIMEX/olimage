#
# Auto-generated on: {{ stamp.date }}
# Generated UUID: {{ stamp.uuid }}
#
# Set default bootargs
{% for key, value in bootargs.items() %}
setenv {{ key }} "{{ value }}"
{% endfor %}

{% if board.soc == 'sun7i-a20' or board.soc == 'sun50i-a64' %}
# Print boot source
itest.b *0x10028 == 0x00 && echo "U-boot loaded from SD"
itest.b *0x10028 == 0x02 && echo "U-boot loaded from eMMC or secondary SD"
itest.b *0x10028 == 0x03 && echo "U-boot loaded from SPI"
echo "Boot script loaded from ${devtype}"
{% endif %}

if test "${devtype}" = "scsi"; then
    boot_dev_type=scsi
    boot_dev_num="${scsi_bootdev}"
else
    boot_dev_type="mmc"
    boot_dev_num="${mmc_bootdev}"
fi

# Load uEnv.txt
for prefix in ${boot_prefixes}; do
    echo "Checking for ${prefix}{{ uenv.file }}..."
    if test -e ${boot_dev_type} ${boot_dev_num}:{{ partitions.boot }} ${prefix}{{ uenv.file }}; then
        load ${boot_dev_type} ${boot_dev_num}:{{ partitions.boot }} {{ uenv.load }} ${prefix}{{ uenv.file }}
        echo "Loaded environment from ${prefix}{{ uenv.file }}"
        env import -t {{ uenv.load }} ${filesize}
    fi
done

# Get partuuid
if test "${devtype}" = "mmc"; then part uuid mmc ${mmc_bootdev}:{{ partitions.root }} partuuid; fi
if test "${devtype}" = "scsi"; then part uuid scsi ${scsi_bootdev}:{{ partitions.root }} partuuid; fi

# Set bootargs
setenv bootargs "root=PARTUUID=${partuuid} rootwait{% for key, value in bootargs.items() %} {{ key }}={{ '${' }}{{ key }}{{ '}' }}{% endfor %} ${optargs}"

if test -n ${load_legacy} && ${load_legacy}; then
    echo "Loading legacy image format..."

    for prefix in ${boot_prefixes}; do
        if test -e ${boot_dev_type} ${boot_dev_num}:{{ partitions.boot }} ${prefix}Image; then
            load ${boot_dev_type} ${boot_dev_num}:{{ partitions.boot }} ${kernel_addr_r} ${prefix}Image
            load ${boot_dev_type} ${boot_dev_num}:{{ partitions.boot }} ${fdt_addr_r} ${fdtfile}
{% if board.arch == 'arm64' %}
            booti ${kernel_addr_r} - ${fdt_addr_r}
{% else %}
            bootz ${kernel_addr_r} - ${fdt_addr_r}
{% endif %}
        fi
    done
fi

# Load kernel.itb
echo "Loading FIT image..."
for prefix in ${boot_prefixes}; do
    if test -e ${boot_dev_type} ${boot_dev_num}:{{ partitions.boot }} ${prefix}{{ fit.file }}; then
        load ${boot_dev_type} ${boot_dev_num}:{{ partitions.boot }} {{ fit.load }} ${prefix}{{ fit.file }}
        if test -n ${boot_config}; then
            bootm {{ fit.load }}#${boot_config}
        else
            bootm {{ fit.load }}
        fi
    fi
done

# Recompile with:
# mkimage -C none -A arm -T script -d /boot/boot.cmd /boot/boot.scr
