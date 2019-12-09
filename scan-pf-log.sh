#!/bin/sh
# Search postfix logfiles for mails from specific user and include full log entry
LOGFILE=$1
LOGSEARCH=$2

if echo $LOGFILE | grep gz; then 
  for i in `sudo zcat ${LOGFILE} | grep -i ${LOGSEARCH} | awk '{print $6}' | cut -d':' -f1 | egrep '^[A-F0-9]'`; do sudo zcat ${LOGFILE} | grep $i; done
else
  for i in `sudo cat ${LOGFILE} | grep -i ${LOGSEARCH} | awk '{print $6}' | cut -d':' -f1 | egrep '^[A-F0-9]'`; do sudo cat ${LOGFILE} | grep $i; done
fi
 
