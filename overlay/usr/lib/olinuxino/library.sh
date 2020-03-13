#!/bin/bash

function get_board
{
    local BOARD=""

    for comp in $(cat "/proc/device-tree/compatible" | tr '\0' '\n'); do
	    if [[ "$comp" == "olimex,"* ]]; then
		    BOARD=$(cut -d',' -f2 <<< $comp)
		    break
	    fi
    done

    echo ${BOARD}
}

function get_soc
{
    local SOC=""

    for comp in $(cat "/proc/device-tree/compatible" | tr '\0' '\n'); do
	    if [[ "$comp" == "allwinner,sun"* ]]; then
		    SOC=$(cut -d',' -f2 <<< $comp)
		    break
	    fi
    done

    echo ${SOC}
}

function get_root_partuuid
{
    local PARTUUID=""

    for arg in $(cat /proc/cmdline); do
        case $arg in
        "root="*)
                UUID=${arg#root=}
                break
            ;;

        *)
            ;;

        esac
    done

    echo ${PARTUUID}
}

function get_root_uuid
{
    local UUID=""

    while read line; do
        _uuid=$(awk '{print $1}' <<< "$line")
        _mount=$(awk '{print $2}' <<< "$line")
        [[ "${_mount}" =~ ^[/]$ ]] && \
            UUID="${_uuid#UUID=}" && \
            break
    done <<< $(grep -v ^# /etc/fstab)

    echo ${UUID}
}

function get_partition_by_uuid
{
    local UUID=$1

    blkid | grep "${UUID#UUID=}" | cut -d':' -f1
}

function get_partition_by_partuuid
{
    local PARTUUID=$1

    blkid | grep "${PARTUUID#PARTUUID=}" | cut -d':' -f1
}

function get_device_by_partition
{
    local PARTITION=$1

     # The following doesn't work on debian sid.
    DEVICE=$(lsblk -n -o PKNAME "${PARTITION}" | head -n1)

    # Try regex expression
    if [[ -z ${DEVICE} ]]; then
        [[ ${PARTITION} =~ "/dev/mmcblk"[0-9]+ ]] || \
        [[ ${PARTITION} =~ "/dev/sd"[a-z] ]] && \
        DEVICE=${BASH_REMATCH[0]}
    else
        DEVICE="/dev/${DEVICE}"
    fi

    echo ${DEVICE}
}

function get_root_partition
{
    local UUID=$(get_root_uuid)

    [[ -z ${UUID} ]] && return ""

     get_partition_by_uuid ${UUID}
}

function get_root_device
{
    local PARTITION=$(get_root_partition)

    [[ -z ${PARTITION} ]] && return ""

    get_device_by_partition ${PARTITION}

}

function get_emmc_device
{
    local ROOT_DEVICE=$(get_root_device)
    lsblk -l | grep "^mmcblk"[[:digit:]][[:digit:]]*[[:space:]] | grep -v ${ROOT_DEVICE#/*/} | awk '{print "/dev/"$1}'
}

function get_device_block_count
{
    blockdev --getsz $1
}

function get_partition_type
{
    local TYPE=""

    for arg in $(blkid | grep "^$1" | cut -d':' -f2); do
        case ${arg} in
        "TYPE="*)
            TYPE=$(sed 's/"//g' <<< ${arg#TYPE=})
            ;;
        *)
            ;;
        esac
    done

    echo ${TYPE}
}

function get_partition_uuid
{
    local UUID=""

    for arg in $(blkid | grep "^$1" | cut -d':' -f2); do
        case ${arg} in
        "UUID="*)
            UUID=$(sed 's/"//g' <<< ${arg#UUID=})
            ;;
        *)
            ;;
        esac
    done

    echo ${UUID}
}

function get_partition_start_block
{
    local START=""
    local DEVICE=$(get_device_by_partition $1)

    while read -r line; do
        grep -q "^$1" <<< "${line}" || continue

        START=$(awk -F' ' '{print $2}' <<< "${line}")
    done <<< "$(fdisk -l "${DEVICE}")"

    echo ${START}
}

function resize_partition
{
    local PARTITION=$1
    local DEVICE=$(get_device_by_partition ${PARTITION})

    local START=$(get_partition_start_block ${PARTITION})
    local COUNT=$(fdisk -l "${DEVICE}" | grep -c "^${DEVICE}p")

    # Commands are different for single and multi-partition devices
    if [[ ${COUNT} -eq 1 ]]; then
        fdisk "${DEVICE}" > /dev/null 2>&1 << __EOF__
d
n
p
1
${START}

w
__EOF__
    else
        fdisk "${DEVICE}" << __EOF__
d
${PARTITION#${DEVICE}p}
n
p
${PARTITION#${DEVICE}p}
${START}

w
__EOF__
    fi
}