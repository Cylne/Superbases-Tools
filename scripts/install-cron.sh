#!/usr/bin/env bash
set -Eeuo pipefail
schedule="${1:-0 2 * * *}"; if [[ "${EUID}" -eq 0 ]]; then SUDO=""; else SUDO="sudo"; fi
tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
printf '%s\n' 'SHELL=/bin/bash' 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' "$schedule root /usr/local/bin/supamigrate backup --label scheduled >> /var/log/supamigrate-cron.log 2>&1" > "$tmp"
$SUDO install -m 0644 "$tmp" /etc/cron.d/supamigrate; echo "Backup schedule installed: $schedule"
