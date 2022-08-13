#!/usr/bin/env bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
  cat <<EOF
Usage: $(
    basename "${BASH_SOURCE[0]}"
  ) [-h] [-f]

Run dmenu-extended tests

Available options:

-h, --help      Print this help and exit
-f, --full      Run full test-suite (requires docker)
EOF
  exit
}

parse_params() {
  full=0
  while :; do
    case "${1-}" in
    -h | --help) usage ;;
    -f | --full) full=1 ;;
    -?*)
      echo "Unknown option: $1"
      exit 1
      ;;
    *) break ;;
    esac
    shift
  done
  args=("$@")
  return 0
}

parse_params "$@"

if [ "${full}" -eq 1 ]; then
  docker build -f ${script_dir}/tests/Dockerfile -t dmenu-extended-test:latest .
  docker run --rm dmenu-extended-test:latest bash -c "cd /home/user/dmenu-extended/src/dmenu_extended && python3 -m pytest ../../tests"
  docker run --rm dmenu-extended-test:latest /home/user/dmenu-extended/tests/system_tests.sh
else
  cd ${script_dir}/src/dmenu_extended
  python3 -m pytest ../../tests
fi
