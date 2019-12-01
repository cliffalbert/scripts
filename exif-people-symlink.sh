#!/bin/bash
PEOPLE_ROOT="$HOME/People/" 
for i in *.jpg *.JPG; do 
	NAMES=$(exiftool -RegionName "$i" | cut -d':' -f2 | sed -e 's/^\ *//')
	FILENAME="$(pwd)/$i"
	echo "$FILENAME - $NAMES" 
	IFS=',' read -r -a NAME <<< "$NAMES"
	for index in "${!NAME[@]}"
	do
	    echo "$index ${NAME[index]}"
	    PERSON="$(echo "${NAME[index]}" | sed -e 's/^\ *//')"
	    PERSONPATH="${PEOPLE_ROOT}${PERSON}"
	    if [ -d "$PERSONPATH" ]; then
		   echo "$PERSONPATH folder exists"
		   ln -s "$FILENAME" "$PERSONPATH/"
	    else
		   echo "$PERSONPATH folder does not exist"
		   mkdir -p "$PERSONPATH"
		   ln -s "$FILENAME" "$PERSONPATH/"
	    fi 
	done
done
