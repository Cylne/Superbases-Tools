#!/usr/bin/env bash

set -Eeuo pipefail

APP_DIR="/opt/Superbases-Tools"
BIN_PATH="/usr/local/bin/supamigrate"

WITH_SUPABASE=false

if [[ "${1:-}" == "--with-supabase-cli" ]]; then
    WITH_SUPABASE=true
fi

if [[ "$(uname -s)" != "Linux" ]] || ! command -v apt-get >/dev/null 2>&1; then
    echo "Error: installer supports Debian/Ubuntu Linux."
    exit 1
fi

if [[ "${EUID}" -eq 0 ]]; then
    SUDO=""
else
    if ! command -v sudo >/dev/null 2>&1; then
        echo "Error: run as root or install sudo."
        exit 1
    fi
    SUDO="sudo"
fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo
echo "=========================================="
echo "        SUPERBASES TOOLS INSTALLER"
echo "=========================================="
echo

echo "[1/6] Installing system dependencies..."

$SUDO apt-get update

$SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    postgresql-client \
    curl \
    ca-certificates \
    tar

echo "[2/6] Installing application..."

$SUDO mkdir -p "$APP_DIR"

# Copy the complete project into one self-contained directory.
# Existing .env and config.json are preserved.
$SUDO cp -a "$SOURCE_DIR/." "$APP_DIR/"

$SUDO mkdir -p \
    "$APP_DIR/backups" \
    "$APP_DIR/logs"

echo "[3/6] Creating Python virtual environment..."

if [[ ! -d "$APP_DIR/.venv" ]]; then
    $SUDO python3 -m venv "$APP_DIR/.venv"
fi

$SUDO "$APP_DIR/.venv/bin/python" -m pip install \
    --disable-pip-version-check \
    --no-cache-dir \
    --upgrade pip

$SUDO "$APP_DIR/.venv/bin/pip" install \
    --disable-pip-version-check \
    --no-cache-dir \
    -r "$APP_DIR/requirements.txt"

echo "[4/6] Preparing configuration..."

if [[ ! -f "$APP_DIR/.env" ]]; then
    if [[ -f "$APP_DIR/.env.example" ]]; then
        $SUDO cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    fi
fi

if [[ ! -f "$APP_DIR/config.json" ]]; then
    if [[ -f "$APP_DIR/config.example.json" ]]; then
        $SUDO cp \
            "$APP_DIR/config.example.json" \
            "$APP_DIR/config.json"
    fi
fi

$SUDO mkdir -p "$APP_DIR/backups"

if [[ -f "$APP_DIR/.env" ]]; then
    $SUDO chmod 600 "$APP_DIR/.env"
fi

if [[ -f "$APP_DIR/config.json" ]]; then
    $SUDO chmod 600 "$APP_DIR/config.json"
fi

echo "[5/6] Installing global command..."

TMP_WRAPPER="$(mktemp)"

cat > "$TMP_WRAPPER" <<EOF
#!/usr/bin/env bash

export SUPAMIGRATE_HOME="$APP_DIR"
export SUPAMIGRATE_CONFIG="\${SUPAMIGRATE_CONFIG:-$APP_DIR/config.json}"

exec "$APP_DIR/.venv/bin/python" \
    "$APP_DIR/supamigrate.py" "\$@"
EOF

$SUDO install -m 0755 \
    "$TMP_WRAPPER" \
    "$BIN_PATH"

rm -f "$TMP_WRAPPER"

echo "[6/6] Validating installation..."

"$BIN_PATH" --help >/dev/null

echo
echo "=========================================="
echo "       INSTALLATION SUCCESSFUL"
echo "=========================================="
echo
echo "Application : $APP_DIR"
echo "Config      : $APP_DIR/config.json"
echo "Environment : $APP_DIR/.env"
echo "Backups     : $APP_DIR/backups"
echo
echo "Commands:"
echo "  supamigrate"
echo "  supamigrate check"
echo "  supamigrate backup"
echo "  supamigrate restore <archive>"
echo "  supamigrate storage"
echo "  supamigrate auth-report"
echo "  supamigrate functions"
echo "  supamigrate retention"
echo
echo "Edit your credentials in:"
echo "  $APP_DIR/.env"
echo
echo "Then run:"
echo "  supamigrate check"
echo

if $WITH_SUPABASE; then
    echo "Installing Supabase CLI..."

    arch="$(dpkg --print-architecture)"

    case "$arch" in
        amd64)
            asset="supabase_linux_amd64.tar.gz"
            ;;
        arm64)
            asset="supabase_linux_arm64.tar.gz"
            ;;
        *)
            echo "Unsupported architecture: $arch"
            exit 1
            ;;
    esac

    release_url="$(
        curl -fsSL \
        https://api.github.com/repos/supabase/cli/releases/latest |
        sed -n \
        's/.*"browser_download_url": "\([^"]*'"$asset"'\)".*/\1/p' |
        head -n1
    )"

    if [[ -z "$release_url" ]]; then
        echo "Unable to resolve Supabase CLI release."
        exit 1
    fi

    TMP_CLI="$(mktemp -d)"

    curl -fsSL "$release_url" \
        -o "$TMP_CLI/cli.tar.gz"

    tar -xzf "$TMP_CLI/cli.tar.gz" \
        -C "$TMP_CLI"

    $SUDO install -m 0755 \
        "$TMP_CLI/supabase" \
        /usr/local/bin/supabase

    rm -rf "$TMP_CLI"

    echo "Supabase CLI installed."
fi
