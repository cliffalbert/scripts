#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
fi

FILENAME=$(mktemp /tmp/tfile.XXXXXXXXXXX)
ACTOR="$1"

find ./ -type f | grep -v nfo > ${FILENAME}

while read i 
    do 
	echo "FILE: $i"
	NFO_FILE=$(echo "$i" | sed -e s/\....$//) 
	echo "NFO_FILE: ${NFO_FILE}.nfo"
echo "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>
<movie>
  <plot />
  <outline />
  <actor>
    <name>${ACTOR}</name>
    <type>Actor</type>
  </actor>
</movie>
" > "${NFO_FILE}".nfo

echo "${NFO_FILE}"

done < ${FILENAME}

rm -f ${FILENAME}

sudo find ./ -iname '*.nfo' -exec chown emby:emby "{}" \;
	
