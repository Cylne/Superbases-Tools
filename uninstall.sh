#!/usr/bin/env bash
set -Eeuo pipefail
if [[ "${EUID}" -eq 0 ]]; then SUDO=""; else SUDO="sudo"; fi
$SUDO rm -f /usr/local/bin/supamigrate /etc/cron.d/supamigrate; $SUDO rm -rf /opt/supamigrate
echo "Application removed. Configuration preserved at /etc/supamigrate."
