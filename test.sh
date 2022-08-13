#!/usr/bin/env bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

set -eu

usage() {
  cat <<EOF
Usage: $(
    basename "${BASH_SOURCE[0]}"
  ) [-h] [-f]

Run dmenu-extended tests

Available options:

-h, --help      Print this help and exit
-f, --full      Run full test-suite (requires docker)
-b, --build     Build the docker image to run system tests (requires docker)
EOF
  exit
}

parse_params() {
  full=0
  build=0
  while :; do
    case "${1-}" in
    -h | --help) usage ;;
    -f | --full) full=1 ;;
    -b | --build) build=1 ;;
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

build_image() {
  docker build -f ${script_dir}/tests/Dockerfile -t dmenu-extended-test:latest .
  return $?
}

parse_params "$@"

if [ "${build}" -eq 1 ] || [ "${full}" -eq 1 ]; then
  if [ "${build}" -eq 1 ]; then
    if ! build_image; then
      echo "Failed to build the image"
      exit 1
    else
      echo "Image built successfully"
    fi
  fi
  if [ "${full}" -eq 1 ]; then
    if [ "$(docker images -q dmenu-extended-test:latest)" = "" ]; then
      echo "Docker image not found. Automatically building it..."
      build_image
    fi
    trap 'docker rmi dmenu-extended-test > /dev/null' EXIT
    docker run --rm dmenu-extended-test:latest bash -c "cd /home/user/dmenu-extended/src/dmenu_extended && python3 -m pytest ../../tests"
    docker run --rm dmenu-extended-test:latest /home/user/dmenu-extended/tests/system_tests.sh
  fi
else
  cd ${script_dir}/src/dmenu_extended
  python3 -m pytest ../../tests
fi
