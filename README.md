# scripts

## Server maintenance and operations
produce-redirect.sh: produce nginx configuration files for URL redirection

backup.sh: remote rsync backup script with hard-link incremental support

backup-clean.sh: clean up backups keeping first of month backups

scan-pf-log.sh: check log entries for specific e-mail adres and show full log

Makefile.postfix: Makefile to reload postfix and generate new .db/maps for postfix

## Letsencrypt Scripts

gen-plex-cert.sh: SSL Certificates for Plex using letsencrypt

gen-unifi-cert.sh: SSL Certificates for Unifi Controller using letsencrypt

## Network Engineering

search_ip.py: Generate overview of an IP address from Netbox

search_tenant_resources_public.py: Generate overview of all prefixes of a tenant from Netbox

## Emby Scripts

update-nfo.sh: script to generate emby .nfo files to set actor/actress for all movies in the directory (works recursive)
nfo-tool.pl: next generation based on update-nfo.sh rewrite in perl
nfo-symlink.sh: if media has been symlinked to another file this will also fix a symlink for the corresponding .nfo file

## Maildir/MUTT scripts

newmaildir.sh: script to do a monthly rotate on a maildir structure

## EXIF/Picture Scripts

exif-people-symlink.sh: extract exif people tag (Picasa) and symlink into persons directory

