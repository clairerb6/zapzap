#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

BUILD_INFO_PATH="zapzap/BuildInfo.py"
BUILD_INFO_BACKUP=""

if [[ -f "${BUILD_INFO_PATH}" ]]; then
  BUILD_INFO_BACKUP="$(mktemp)"
  cp "${BUILD_INFO_PATH}" "${BUILD_INFO_BACKUP}"
fi

cleanup_build_info() {
  if [[ -n "${BUILD_INFO_BACKUP}" && -f "${BUILD_INFO_BACKUP}" ]]; then
    cp "${BUILD_INFO_BACKUP}" "${BUILD_INFO_PATH}"
    rm -f "${BUILD_INFO_BACKUP}"
  else
    rm -f "${BUILD_INFO_PATH}"
  fi
}

trap cleanup_build_info EXIT

rm *.deb -f
rm deb_build -Rf

VERSION="$(python3 - <<'PY'
import ast
from pathlib import Path

module = Path("zapzap/__init__.py")
tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))

for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                value = ast.literal_eval(node.value)
                print(value)
                raise SystemExit(0)

raise SystemExit("Could not find __version__ in zapzap/__init__.py")
PY
)"

BUILD_REPOSITORY="$(git config --get remote.origin.url || true)"
BUILD_REPOSITORY="${BUILD_REPOSITORY:-https://github.com/clairerb6/zapzap.git}"

BUILD_CHANNEL="DEB" \
BUILD_PROVIDER="clairerb6 Debian package" \
BUILD_REPOSITORY="${BUILD_REPOSITORY}" \
python3 - <<'PY'
from builders.common import create_build_info

create_build_info()
PY

mkdir -p deb_build/usr/local/bin deb_build/usr/share/zapzap deb_build/DEBIAN
mkdir -p deb_build/usr/share/applications
mkdir -p deb_build/usr/share/icons/hicolor/scalable/apps
mkdir -p deb_build/usr/share/metainfo

cat << 'EOF' > deb_build/usr/local/bin/zapzap
#!/usr/bin/env bash
cd /usr/share/zapzap
python3 -m zapzap
EOF

chmod +x deb_build/usr/local/bin/zapzap

cp share/applications/com.rtosta.zapzap.desktop deb_build/usr/share/applications/
cp share/icons/com.rtosta.zapzap.svg deb_build/usr/share/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg
cp share/metainfo/com.rtosta.zapzap.appdata.xml deb_build/usr/share/metainfo/

cat << EOF > deb_build/DEBIAN/control
Package: zapzap
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt6.qtwebengine, python3-dbus
Maintainer: Katherine Flores <me@katherineflores.me>
Description: ZapZap - Cliente no oficial de WhatsApp Web para Linux.
EOF

rsync -a \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  zapzap \
  LICENSE \
  README.md \
  requirements.txt \
  pyproject.toml \
  deb_build/usr/share/zapzap/

dpkg-deb --root-owner-group --build deb_build

mv deb_build.deb zapzap_${VERSION}_amd64.deb
