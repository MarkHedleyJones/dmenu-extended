#!/usr/bin/env bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

set -eu

build_image() {
  docker build -f ${script_dir}/tests/Dockerfile -t dmenu-extended-test:latest .
  return $?
}

task() {
  echo "${1} ..."
}

error() {
  echo " ✗ - ${1}"
}

success() {
  echo " ✓ - ${1}"
}

usage() {
  cat <<EOF
Usage: $(
    basename "${BASH_SOURCE[0]}"
  ) [-h] [-f]

Run dmenu-extended tests

Available options:

-b, --build          Build the docker image to run system tests (requires docker)
-c, --check-version  Check that the version defined in pyproject.toml is higher than that listed on pypi
-h, --help           Print this help and exit
-l, --lint           Check the code using flake8 and black
-s, --system         Run all tests (requires docker)
-p, --performance    Run a performance test (requires docker)

EOF
  exit
}

parse_params() {
  build=0
  check_version=0
  format=0
  lint=0
  performance=0
  system=0
  while :; do
    case "${1-}" in
    -b | --build) build=1 ;;
    -c | --check-version) check_version=1 ;;
    -h | --help) usage ;;
    -l | --lint) lint=1 ;;
    -p | --performance) performance=1 ;;
    -s | --system) system=1 ;;
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
    success "The version in pyproject.toml (${version}) has been correctly incremented relative to the version on pypi (${pypi_version})"
    exit 0
  else
    error "The version in pyproject.toml (${version}) has not been incremented relative to the current version on pypi (${pypi_version})"
    exit 1
  fi
fi
if [ "${build}" -eq 1 ] || [ "${system}" -eq 1 ] || [ "${lint}" -eq 1 ] || [ "${performance}" -eq 1 ]; then
  image_hash="$(docker images -q dmenu-extended-test:latest)"
  if [ "${build}" -eq 1 ] || [ "${image_hash}" = "" ]; then
    if [ "${image_hash}" = "" ]; then
      task "Docker image not found - building"
    fi
    if ! build_image; then
      error "Failed to build the image"
      exit 1
    else
      success "Image built successfully"
    fi
  fi
  if [ "${system}" -eq 1 ] || [ "${lint}" -eq 1 ] || [ "${performance}" -eq 1 ]; then
    trap 'docker rmi dmenu-extended-test > /dev/null' EXIT
    if [ "${lint}" -eq 1 ]; then
      linter="flake8"
      task "Checking code with ${linter}"
      if ! docker run --rm dmenu-extended-test:latest bash -c "cd dmenu-extended && ${linter} ./src/dmenu_extended"; then
        error "Linting with ${linter} failed"
        exit 1
      else
        success "Linting with ${linter} was successful"
      fi
    fi
    if [ "${system}" -eq 1 ]; then
      docker run --rm dmenu-extended-test:latest bash -c "cd /home/user/dmenu-extended/src/dmenu_extended && python3 -m pytest ../../tests"
      docker run --rm dmenu-extended-test:latest /home/user/dmenu-extended/tests/system_tests.sh
    fi
    if [ "${performance}" -eq 1 ]; then
      docker run --rm dmenu-extended-test:latest /home/user/dmenu-extended/tests/performance_test.sh
    fi
  fi
else
  cd ${script_dir}/src/dmenu_extended
  python3 -m pytest ../../tests
fi
