#!/bin/bash
#
#
# BACKUP Script
#
#
# backup.sh <remote host> <remote path> <local path> 
#
#
REMOTE_HOST=$1
REMOTE_PATH=$2
LOCAL_PATH=$3

if [ ! -d $LOCAL_PATH ]; then
  echo "Local path $LOCAL_PATH does not exist"
  exit
fi

#
OLDEST_BACKUP=$(ls $LOCAL_PATH | egrep -v '20..-..-01' | head -1)
OLDEST_BACKUP_PATH="$LOCAL_PATH/$OLDEST_BACKUP"
LAST_BACKUP=$(ls -t $LOCAL_PATH | head -1)
LAST_BACKUP_PATH="$LOCAL_PATH/$LAST_BACKUP"

if [ ! -d $OLDEST_BACKUP_PATH ]; then
  echo "Local last backup is invalid"
  exit
fi

logger -t backup "backup-clean $OLDEST_BACKUP_PATH start"

if [ $(ls $LOCAL_PATH | egrep -v '20..-..-01' | wc -l) -gt 10 ]; then 

  echo "Removing $OLDEST_BACKUP_PATH"
  rm -rf $OLDEST_BACKUP_PATH

else
 
 echo "Not enough backups in $LOCAL_PATH ;minimum of 10 required"

fi

logger -t backup "backup-clean $OLDEST_BACKUP_PATH stop"

