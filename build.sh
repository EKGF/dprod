#!/usr/bin/env bash
#
# Execute this from your document repo's root
#
REPO_DIR="$(dirname $(realpath ${BASH_SOURCE[0]}))"
dist_dir="${REPO_DIR}/dist"
venv_dir="${REPO_DIR}/.venv"
system_python_bin="/usr/bin/python3"
venv_python_bin="${venv_dir}/bin/python3"

function setup() {

  mkdir -p "${dist_dir}" >/dev/null 2>&1 || return $?
  
  ${system_python_bin} -m venv ${venv_dir} || return $?

	source .venv/bin/activate
	${venv_python_bin} -m pip install --upgrade pip || return $?
	${venv_python_bin} -m pip install -r requirements.txt || return $?

  return 0  
}

function build() {

  source ${venv_dir}/bin/activate || return $?
  
  ${venv_python_bin} spec-generator.py || return $?

  return 0
}

function main() {

  setup || return $?
  
  build || return $?

  return 0
}

main
exit $?
