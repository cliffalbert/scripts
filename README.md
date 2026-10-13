# scripts

This is a mirror of the original git repo in my personal forgejo

https://oisec.net/

Destructive scripts (delete or overwrite data): `backup-clean.sh`, `orphan-nfo.sh`, `rename-ascii.py`, `rtorrent-check.py`, `update-nfo.sh`.

## Server maintenance and operations

produce-redirect.sh: produce nginx configuration files for URL redirection

backup.sh: remote rsync backup script with hard-link incremental support. Usage: `backup.sh <remote host> <remote path> <local path>`. Requires an existing snapshot directory under the local path to use as `--link-dest`.

backup-clean.sh: remove the oldest non-monthly snapshot when more than 10 remain. First-of-month directories (`YYYY-MM-01…`) are kept. Usage: `backup-clean.sh <local path>` or the same 3 args as `backup.sh`.

scan-pf-log.sh: check log entries for specific e-mail adres and show full log

Makefile.postfix: Makefile to reload postfix and generate new .db/maps for postfix

ssdstor-enclosure-leds: map md/RAID devices to SAS enclosure slots, SMART-check drives, set fault LEDs (root)

ssdstor-enclosure-leds-zfs: same as above for ZFS pools instead of md

## Letsencrypt Scripts

gen-plex-cert.sh: SSL Certificates for Plex using letsencrypt. Requires `PLEX_KEYFILE_PASS` (PKCS12 / Plex custom certificate encryption key). The old hardcoded password was committed to git — treat it as compromised, export a new secret, and set the same value in Plex.

gen-unifi-cert.sh: SSL Certificates for Unifi Controller using letsencrypt

## Network Engineering

search_ip.py: Generate overview of an IP address from Netbox

search_tenant_resources_public.py: Generate overview of all prefixes of a tenant from Netbox

## Emby Scripts

update-nfo.sh: generate emby .nfo files to set actor/actress for all movies in the directory (recursive). Overwrites existing `.nfo` sidecars.

nfo-tool.pl: patch an existing `.nfo` (year, actor, studio, tags) without regenerating the whole file. Use this to update; use `update-nfo.sh` to create.

nfo-symlink.sh: if media has been symlinked to another file this will also fix a symlink for the corresponding .nfo file

orphan-nfo.sh: find `.nfo` files with no matching media sidecar and rename them to `.nfo.backup`

gen-actor-pair-graphviz.sh: emit Graphviz edges for actor pairs found in `/opt/**/*.nfo`

## Maildir/MUTT scripts

newmaildir.sh: script to do a monthly rotate on a maildir structure

## EXIF/Picture Scripts

exif-people-symlink.sh: extract exif people tag (Picasa) and symlink into persons directory

rename-ascii.py: strip non-ASCII characters from filenames in the current directory

## Ansible / AWX / AAP

awx-check.py: extracts all job templates with configured limits. Token via `AWX_TOKEN` or `--token`; URL via `AWX_URL`.

awx-inventory.py: dump AWX inventories as an Ansible YAML inventory. Each AWX inventory is a child group, with its host groups kept. Disabled hosts are omitted. Host descriptions come from AWX; a host with none is marked "Auto Added by AWX Inventory". Token via `AWX_TOKEN` or `--token`; URL via `AWX_URL`.

## Torrents

gen-torrent-hash.py: print infohash for `example.torrent` via libtorrent (stub)

rtorrent-check.py: verify a torrent against `/media/torrent/unsorted/` and delete the rtorrent job if files are missing
