# AGENTS.md

Personal ops/media scripts. Mixed Bash, Python 3, and one Perl file. There is no build, test suite, or package manager.

## Quality bar

`awx-check.py` is the reference for new or rewritten tools: argparse, env-var config, timeouts on HTTP, no secrets in source, `if __name__ == "__main__"`.

Shell scripts should use `set -euo pipefail` and quote every expansion. Prefer `#!/usr/bin/env python3` and `#!/usr/bin/env bash` for new files.

Keep changes scoped to the script being asked about. Do not “upgrade” neighboring scripts or reformat for style.

## Secrets

Never commit passwords, API tokens, or keystore passphrases.

| Secret | Where it belongs |
|---|---|
| Plex PKCS12 / custom certificate password | `PLEX_KEYFILE_PASS` |
| AWX URL / token / user / password | `AWX_URL`, `AWX_TOKEN`, `AWX_USERNAME`, `AWX_PASSWORD` |
| NetBox URL / token | env vars or local config — `search_ip.py` and `search_tenant_resources_public.py` still have `url='URL', token='TOKEN'` placeholders |

`gen-plex-cert.sh` previously hardcoded `mekkermekkermekker`. That value is compromised. Require a new `PLEX_KEYFILE_PASS` and the same value in Plex (Settings → Network → Custom certificate encryption key).

UniFi `aircontrolenterprise` is the well-known default keystore password, not a unique secret.

## Destructive scripts

Do not run these against real data from an agent session unless the user explicitly asks and the path is unambiguous.

| Script | What it mutates |
|---|---|
| `backup-clean.sh` | `rm -rf` of snapshot directories |
| `backup.sh` | writes a new snapshot under the local path |
| `orphan-nfo.sh` | `mv` of `.nfo` to `.nfo.backup` |
| `rename-ascii.py` | `os.rename` of every name in `.` |
| `rtorrent-check.py` | deletes `.torrent`, `.rtorrent`, `.libtorrent_resume` |
| `update-nfo.sh` | overwrites `.nfo` sidecars for every non-nfo file |
| `ssdstor-enclosure-leds*` | writes enclosure `fault` sysfs |

`backup-clean.sh` will not delete a path that is the local root itself, and it keeps directories whose names contain `YYYY-MM-01`.

## Script map

- **Backups:** `backup.sh` (rsync `--link-dest`), `backup-clean.sh` (retain first-of-month). Both log via `logger -t backup`. Exclude file is `/backup/backup.exclude`. `backup.sh` needs an existing snapshot dir to link against (first run is not empty-dir safe).
- **Mail / web:** `scan-pf-log.sh`, `Makefile.postfix`, `newmaildir.sh`, `produce-redirect.sh` (writes `/etc/nginx/sites-enabled`).
- **Certs:** `gen-plex-cert.sh`, `gen-unifi-cert.sh` (Let’s Encrypt standalone on :80, then install into Plex PKCS12 / UniFi keystore).
- **NetBox:** `search_ip.py`, `search_tenant_resources_public.py`.
- **AWX:** `awx-check.py` (job template limits), `awx-inventory.py` (YAML inventory dump).
- **Emby NFO:** `update-nfo.sh` creates; `nfo-tool.pl` patches one file (`--nfo`, `--actor`, `--year`, `--studio`, `--tag`); `nfo-symlink.sh` links sidecar NFOs for symlinked media; `orphan-nfo.sh` finds NFOs with no media; `gen-actor-pair-graphviz.sh` prints `GV:` lines from `/opt/**/*.nfo`.
- **Photos:** `exif-people-symlink.sh`, `rename-ascii.py`.
- **Torrents:** `gen-torrent-hash.py` (stub, hardcoded `example.torrent`), `rtorrent-check.py`.
- **Hardware:** `ssdstor-enclosure-leds` (md), `ssdstor-enclosure-leds-zfs` (ZFS). Root required.

## Conventions when editing

- Preserve CLI compatibility unless the user asks to change it. `backup-clean.sh` accepts 1 arg (local path) or the same 3 args as `backup.sh`.
- `nfo-tool.pl` is line-oriented regex over Emby-style one-line XML tags, not a real XML parser. Keep it that way unless asked to rewrite.
- README.md lists every script; update it when adding or renaming files.
- No tests. Syntax-check instead: `bash -n`, `perl -c`, `python3 -m py_compile`.
