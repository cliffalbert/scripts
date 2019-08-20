#!/bin/sh
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
BACKUP_DATE=$(date +%F-%T)
LAST_BACKUP=$(ls -t $LOCAL_PATH | head -1)
LAST_BACKUP_PATH="$LOCAL_PATH/$LAST_BACKUP"
NEW_BACKUP_PATH="$LOCAL_PATH/$BACKUP_DATE"

if [ ! -d $LAST_BACKUP_PATH ]; then
  echo "Local last backup is invalid"
  exit
fi

logger -t backup "backup $NEW_BACKUP_PATH start"

echo "Backup $REMOTE_HOST:$REMOTE_PATH on $BACKUP_DATE to $LOCAL_PATH ($NEW_BACKUP_PATH)"
echo " - rsync $LAST_BACKUP_PATH / $NEW_BACKUP_PATH"
rsync -av --exclude-from=/backup/backup.exclude --numeric-ids --link-dest=$LAST_BACKUP_PATH $REMOTE_HOST:$REMOTE_PATH $NEW_BACKUP_PATH

touch $NEW_BACKUP_PATH

# Sometimes rsync fails to connect and you end up with a file instead of a directory
# This will make sure it gets removed so the next backup wont fail automatically
#
if [ -f $NEW_BACKUP_PATH ]; then
	echo "ERROR: Something went wrong while backing up"
	rm $NEW_BACKUP_PATH
fi

logger -t backup "backup $NEW_BACKUP_PATH stop"

