#!/bin/bash

# Usage:
# adb-push <directory-on-computer-to-send> <directory-on-device-to-receive-it>
# Example:
# adb-push ~/backups/DCIM /sdcard

src="${1}";
trgt="$(basename ${1})";
device="${3}
dst="$(echo "${2}" | grep '/$')";
# If ${dst} ends with '/', remove the trailing '/'.
if [ -n "${dst}" ]; then
    dst="${dst%/*}";
fi;

# If ${src} is a directory, make directories on device before pushing them.
if [ -d "${src}" ]; then
    cd "${src}";
    cd ..;
    trgt="${trgt}/";
    find "${trgt}" -type d -exec adb shell -s "${device}" mkdir "${dst}/{}" \;
fi;

adb push "${src}" "${dst}/${trgt}";
