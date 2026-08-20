#!/bin/bash
#
# backup.sh <remote host> <remote path> <local path>
#
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <remote host> <remote path> <local path>" >&2
  exit 1
fi

REMOTE_HOST=$1
REMOTE_PATH=$2
LOCAL_PATH=$3

if [ ! -d "$LOCAL_PATH" ]; then
  echo "Local path $LOCAL_PATH does not exist" >&2
  exit 1
fi

BACKUP_DATE=$(date +%F-%T)
NEW_BACKUP_PATH="$LOCAL_PATH/$BACKUP_DATE"

LAST_BACKUP_PATH=""
newest=0
shopt -s nullglob
for path in "$LOCAL_PATH"/*; do
  [ -d "$path" ] || continue
  mtime=$(stat -c '%Y' -- "$path")
  if [ "$mtime" -ge "$newest" ]; then
    newest=$mtime
    LAST_BACKUP_PATH=$path
  fi
done

if [ -z "$LAST_BACKUP_PATH" ] || [ ! -d "$LAST_BACKUP_PATH" ] || [ "$LAST_BACKUP_PATH" -ef "$LOCAL_PATH" ]; then
  echo "Local last backup is invalid" >&2
  exit 1
fi

trap 'logger -t backup "backup $NEW_BACKUP_PATH failed"' ERR
logger -t backup "backup $NEW_BACKUP_PATH start"

echo "Backup $REMOTE_HOST:$REMOTE_PATH on $BACKUP_DATE to $LOCAL_PATH ($NEW_BACKUP_PATH)"
echo " - rsync $LAST_BACKUP_PATH / $NEW_BACKUP_PATH"
rsync -av --exclude-from=/backup/backup.exclude --numeric-ids \
  --link-dest="$LAST_BACKUP_PATH" \
  "$REMOTE_HOST:$REMOTE_PATH" "$NEW_BACKUP_PATH"

touch -- "$NEW_BACKUP_PATH"

logger -t backup "backup $NEW_BACKUP_PATH stop"
