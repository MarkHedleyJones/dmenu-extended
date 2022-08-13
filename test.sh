#!/usr/bin/env bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

set -eu

build_image() {
  docker build -f ${script_dir}/tests/Dockerfile -t dmenu-extended-test:latest .
  return $?
}

usage() {
  cat <<EOF
Usage: $(
    basename "${BASH_SOURCE[0]}"
  ) [-h] [-f]

Run dmenu-extended tests

Available options:

-h, --help           Print this help and exit
-f, --full           Run full test-suite (requires docker)
-b, --build          Build the docker image to run system tests (requires docker)
-c, --check-version  Check that the version defined in pyproject.toml is higher than that listed on pypi
EOF
  exit
}

parse_params() {
  full=0
  build=0
  check_version=0
  while :; do
    case "${1-}" in
    -h | --help) usage ;;
    -f | --full) full=1 ;;
    -b | --build) build=1 ;;
    -c | --check-version) check_version=1 ;;
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

if [ "${check_version}" -eq 1 ]; then
  version=$(grep -E '^version =' ${script_dir}/pyproject.toml | cut -d '"' -f 2)
  pypi_version=$(curl -s https://pypi.org/pypi/dmenu-extended/json | jq -r '.info.version')
  if ${script_dir}/tests/check_version_string.sh "${version}" "${pypi_version}"; then
    echo "The version in pyproject.toml (${version}) has been correctly incremented relative to the version on pypi (${pypi_version})"
    exit 0
  else
    echo "The version in pyproject.toml (${version}) has not been incremented relative to the current version on pypi (${pypi_version})"
    exit 1
  fi
fi
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
