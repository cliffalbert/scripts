#!/bin/bash
echo "GV: strict graph {"
find /opt -name '*.nfo' | while read F; do

  echo " * Processing $F ... "
  declare -i COUNT=0
  declare -a ACTOR
  while read A; do
    COUNT=COUNT+1
    echo "   * Processing actor $A ($COUNT) ... "
    SANA="$(echo $A | sed -e 's/\.//g')"
    ACTOR[${COUNT}]="$SANA";
  done < <(cat "$F" | grep 'name' | sed -e 's#^\ *<name>##' | sed -e 's#</name>.*$##')

  echo " * Total Actors: $COUNT"

  if [ $COUNT -gt 1 ]; then
  declare -i RUN=1
  while [ "x${ACTOR[RUN]}" != "x" ]
  do
    declare -i SUBSET=1
    while [ "x${ACTOR[SUBSET]}" != "x" ]
    do 
      if [ $SUBSET != $RUN ]; then
        echo "GV: \"${ACTOR[RUN]}\" -- \"${ACTOR[SUBSET]}\"";
      fi
      SUBSET=SUBSET+1
    done 
    RUN=RUN+1
  done
  fi

  unset ACTOR
done
echo "GV: }"
