#!/bin/sh

FILE=$1

if [ -e "${FILE}" ]; then
	echo "P: ${FILE}"
	if [ -h "${FILE}" ]; then
		TARGET_FILE=$(readlink "${FILE}")
		echo "T: ${TARGET_FILE}"
		BASE_NAME="${FILE%.*}"
		echo "B1: ${BASE_NAME}"
		BASE_NAME_TARGET="${TARGET_FILE%.*}"
		echo "B2: ${BASE_NAME_TARGET}"
		NFO="${BASE_NAME}.nfo" 
		NFO_TARGET="${BASE_NAME_TARGET}.nfo"
		if [ -f "${NFO_TARGET}" ]; then
			echo "N2: ${NFO_TARGET}"
			if [ -e "${NFO}" ]; then
				echo "NFO source exists"
				diff -u "${NFO}" "${NFO_TARGET}"
				exit 2
			else
				ln -s "${NFO_TARGET}" "${NFO}"
				echo "Linked ${NFO_TARGET} to ${NFO}"
				exit 0
			fi
		else
			echo "No NFO target exists"
			exit 2
		fi
	fi
else
	echo "E: Invalid file ${FILE}"
fi
