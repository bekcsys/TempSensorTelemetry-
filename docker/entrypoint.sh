#!/bin/sh
# On up: archive any existing CSVs, then publish a new file.
# Charts are written on the host by make stop.
set -e

export MPLCONFIGDIR=/tmp/matplotlib

sync_visualize_output_owner() {
  target=/app/Visualize/output
  ref=/app/exports
  mkdir -p "${target}"
  if [ -d "${ref}" ]; then
    owner=$(stat -c '%u:%g' "${ref}" 2>/dev/null || true)
    if [ -n "${owner}" ]; then
      chown -R "${owner}" "${target}" 2>/dev/null || true
    fi
  fi
}

sync_visualize_output_owner

archive_csv() {
  python -c "from mqtt_csv_logger import archive_csv_exports; paths = archive_csv_exports(); print(f'Archived {len(paths)} CSV file(s)', flush=True)"
}

plot_latest_csv() {
  return 0
}

archive_csv

term_handler() {
  if [ -n "${child:-}" ]; then
    kill -TERM "${child}" 2>/dev/null || true
    wait "${child}" 2>/dev/null || true
  fi
  plot_latest_csv || true
  exit 0
}

trap term_handler TERM INT

python -u mqtt_publisher.py &
child=$!
wait "${child}"
