#!/bin/bash
#
# backup-clean.sh <local path>
# backup-clean.sh <remote host> <remote path> <local path>
#
# Removes the oldest non-monthly snapshot when more than 10 remain.
# Directories whose names contain YYYY-MM-01 (first of month) are kept.
#
set -euo pipefail

usage() {
  echo "Usage: $0 <local path>" >&2
  echo "   or: $0 <remote host> <remote path> <local path>" >&2
  exit 1
}

if [ "$#" -eq 1 ]; then
  LOCAL_PATH=$1
elif [ "$#" -eq 3 ]; then
  LOCAL_PATH=$3
else
  usage
fi

if [ ! -d "$LOCAL_PATH" ]; then
  echo "Local path $LOCAL_PATH does not exist" >&2
  exit 1
fi

# Lexical order matches chronological order for YYYY-MM-DD-* names.
OLDEST_BACKUP=""
NON_MONTHLY_COUNT=0
shopt -s nullglob
for path in "$LOCAL_PATH"/*; do
  [ -e "$path" ] || continue
  name=$(basename -- "$path")
  if [[ ! "$name" =~ 20[0-9][0-9]-[0-9][0-9]-01 ]]; then
    NON_MONTHLY_COUNT=$((NON_MONTHLY_COUNT + 1))
    if [ -z "$OLDEST_BACKUP" ]; then
      OLDEST_BACKUP=$name
    fi
  fi
done

if [ -z "$OLDEST_BACKUP" ]; then
  echo "No non-monthly backup to remove in $LOCAL_PATH"
  exit 0
fi

OLDEST_BACKUP_PATH="$LOCAL_PATH/$OLDEST_BACKUP"

if [ ! -d "$OLDEST_BACKUP_PATH" ]; then
  echo "Oldest backup path is invalid: $OLDEST_BACKUP_PATH" >&2
  exit 1
fi

# Refuse to delete LOCAL_PATH itself if OLDEST_BACKUP were empty or '.'
if [ "$OLDEST_BACKUP_PATH" -ef "$LOCAL_PATH" ]; then
  echo "Refusing to delete $OLDEST_BACKUP_PATH (same as local path)" >&2
  exit 1
fi

case "$OLDEST_BACKUP_PATH" in
  "$LOCAL_PATH"/*) ;;
  *)
    echo "Refusing to delete path outside $LOCAL_PATH: $OLDEST_BACKUP_PATH" >&2
    exit 1
    ;;
esac

logger -t backup "backup-clean $OLDEST_BACKUP_PATH start"

if [ "$NON_MONTHLY_COUNT" -gt 10 ]; then
  echo "Removing $OLDEST_BACKUP_PATH"
  rm -rf -- "$OLDEST_BACKUP_PATH"
else
  echo "Not enough backups in $LOCAL_PATH ;minimum of 10 required"
fi

logger -t backup "backup-clean $OLDEST_BACKUP_PATH stop"
