#!/bin/sh
#
# find orphaned .nfo files
#
TMPFILE=$(mktemp /tmp/orphan.XXXX)

echo "Using TMP ${TMPFILE}"

find ./ -type f -iname '*.nfo' > ${TMPFILE}

COUNT=$(wc -l ${TMPFILE} | awk '{print $1}')

echo " - Going to analyze ${COUNT} .nfo files"

cat ${TMPFILE} | while read LINE; do
    COUNT_LINE=$(( $COUNT_LINE + 1))
    LINE_CLEAR=${LINE%.nfo}
    RESULT=$(ls "${LINE_CLEAR}".* | egrep -v '\.nfo$' | head -1)
    if [ -z "${RESULT}" ]; then
	   COUNT_MISSING=$(( $COUNT_MISSING + 1 ))
	   mv "${LINE}" "${LINE}.backup"
    else  
           COUNT_FOUND=$(( $COUNT_FOUND + 1))
    fi

    /bin/echo -en "Progress (M/F/C/T) ${COUNT_MISSING}/${COUNT_FOUND}/${COUNT_LINE}/${COUNT}\r"

done


echo "Progress (M/F/C/T) ${COUNT_MISSING}/${COUNT_FOUND}/${COUNT_LINE}/${COUNT}"
