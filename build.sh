#!/usr/bin/env bash
#
# Execute this from your document repo's root
#
REPO_DIR="$(dirname "$(realpath ${BASH_SOURCE[0]})")"
venv_dir="${REPO_DIR}/.venv"
system_python_bin="/usr/bin/python3"
system_python_version="0.0.0"
system_python_minimum_version="3.12"
venv_python_bin="${venv_dir}/bin/python${system_python_minimum_version}"

function check_system_python() {
  if which "python${system_python_minimum_version}" >/dev/null 2>&1 ; then
    system_python_bin=$(which "python${system_python_minimum_version}")
  fi
  if [ ! -x "${system_python_bin}" ]; then
    echo "Python not found at ${system_python_bin}"
    return 1
  fi
  system_python_version="$("${system_python_bin}" --version 2>&1 | cut -c8-)"
  IFS="." read major minor patch <<< ${system_python_version}
  IFS="." read min_major min_minor min_patch <<< ${system_python_minimum_version}
  if ((major == min_major && minor == min_minor)); then
    echo "Python ${system_python_version} is installed"
  else  
    echo "We need Python ${system_python_minimum_version} or higher, not ${system_python_version}"
    if which brew >/dev/null 2>&1 ; then
      echo "You can install Python ${system_python_minimum_version} with Homebrew by running:"
      echo "brew install python@${system_python_minimum_version}"
      echo "We're now going to try to install it for you using the above command"
      brew install python@${system_python_minimum_version} || return $?
      check_system_python || return $?
    fi
    return 1
  fi
  return 0
}

function setup() {

  rm -rf dist > /dev/null 2>&1

  check_system_python || return $?  
  
  "${system_python_bin}" -m venv --upgrade --upgrade-deps "${venv_dir}" || return $?

	# shellcheck disable=SC2086
	source ${venv_dir}/bin/activate
	
	"${venv_python_bin}" -m pip install --upgrade pip || return $?
	"${venv_python_bin}" -m pip install -r requirements.txt || return $?

  return 0  
}

function build() {

  source ${venv_dir}/bin/activate || return $?
  
  ${venv_python_bin} spec-generator/main.py || return $?

  return 0
}

function main() {

  setup || return $?
  
  build || return $?

  return 0
}

main
exit $?
