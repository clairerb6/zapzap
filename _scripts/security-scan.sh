#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

REPORT_DIR="${REPO_ROOT}/security-reports"
VENV_DIR="${REPO_ROOT}/.venv-security-scan"

PIP_AUDIT_FAILED=0
BANDIT_FAILED=0
TRIVY_FAILED=0
TRIVY_SKIPPED=0

mkdir -p "${REPORT_DIR}"

echo "==> Security scan started"
echo "==> Reports directory: ${REPORT_DIR}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required."
  exit 2
fi

echo "==> Creating virtual environment: ${VENV_DIR}"
python3 -m venv "${VENV_DIR}"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "==> Installing scan dependencies"
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt pip-audit bandit >/dev/null

echo "==> Running pip-audit"
if pip-audit -r requirements.txt -f json -o "${REPORT_DIR}/pip-audit.json"; then
  echo "pip-audit: OK"
else
  echo "pip-audit: vulnerabilities found"
  PIP_AUDIT_FAILED=1
fi

echo "==> Running bandit"
if bandit -r zapzap -f json -o "${REPORT_DIR}/bandit.json"; then
  echo "bandit: OK"
else
  echo "bandit: issues found"
  BANDIT_FAILED=1
fi

echo "==> Running trivy (filesystem scan)"
if command -v trivy >/dev/null 2>&1; then
  if trivy fs --format json --output "${REPORT_DIR}/trivy-fs.json" .; then
    echo "trivy: OK"
  else
    echo "trivy: vulnerabilities found"
    TRIVY_FAILED=1
  fi
else
  echo "trivy: not installed, skipping"
  TRIVY_SKIPPED=1
fi

echo
echo "==> Summary"
echo "pip-audit failed: ${PIP_AUDIT_FAILED}"
echo "bandit failed: ${BANDIT_FAILED}"
echo "trivy failed: ${TRIVY_FAILED}"
echo "trivy skipped: ${TRIVY_SKIPPED}"
echo "reports: ${REPORT_DIR}"

if [[ "${PIP_AUDIT_FAILED}" -eq 1 || "${BANDIT_FAILED}" -eq 1 || "${TRIVY_FAILED}" -eq 1 ]]; then
  exit 1
fi

exit 0
