#!/usr/bin/env bash
<<EOF

   Tool \ Shell Scripts \ Run \ Tool

   Run the tool from this repository.

EOF
CURRENT_SCRIPT_DIRECTORY=${CURRENT_SCRIPT_DIRECTORY:-$(dirname $(realpath ${BASH_SOURCE[0]:-${(%):-%x}}))}
export SHARED_EXT_SCRIPTS_PATH=${SHARED_EXT_SCRIPTS_PATH:-$(realpath $CURRENT_SCRIPT_DIRECTORY)}
export CURRENT_SCRIPT_FILENAME=${CURRENT_SCRIPT_FILENAME:-$(basename ${BASH_SOURCE[0]:-${(%):-%x}})}
export CURRENT_SCRIPT_FILENAME_BASE=${CURRENT_SCRIPT_FILENAME%.*}
. "$SHARED_EXT_SCRIPTS_PATH/shared_functions.sh"
write_header

cleanup_virtualenv() {
    write_info "run" "Cleaning up ($1)"
    deactivate
    rm -rf $CURRENT_SCRIPT_DIRECTORY/venv
    exit 0
}

cleanup_pipx() {
    echo "Cleaning up temporary files..."
    rm -f /tmp/my_temp_file
}

if ! is_command_available python; then
    write_error "run" "Failed: Unable to find \"python\" installed on this system. Unable to continue."
    exit 1
fi

if [ ! -e "$CURRENT_SCRIPT_DIRECTORY/.python-version" ]; then
    write_error "run" "Failed: Unable to locate the target Python version on disk."
    exit 1
fi

CURRENT_PYTHON_VERSION=$(python --version | cut -d ' ' -f2)
PROJECT_PYTHON_VERSION=$(<"$CURRENT_SCRIPT_DIRECTORY/.python-version")

if [[ ! "$PROJECT_PYTHON_VERSION" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
    write_error "run" "The project version is not a valid semantic version".
    exit 1
fi

if [ -z "$PROJECT_PYTHON_VERSION" ]; then
    write_error "run" "The Python version was not defined or is empty."
fi

write_info "run" "Python Version: \"$PROJECT_PYTHON_VERSION\""
write_info "run" "Current Python Version: \"$CURRENT_PYTHON_VERSION\""

if [[ ! $PROJECT_PYTHON_VERSION != *"$CURRENT_PYTHON_VERSION"* ]]; then
    write_error "run" "Python $PROJECT_PYTHON_VERSION is not present from the command-line. Check your configuration and try again."
    exit 1
fi

if is_command_available virtualenv; then
    write_info "run" "\"virtualenv\" was found on this system."
    if [ ! -d "$CURRENT_SCRIPT_DIRECTORY/venv" ]; then
        trap 'cleanup_virtualenv EXIT' EXIT
        python -m virtualenv $CURRENT_SCRIPT_DIRECTORY/bin/venv
        pip install .

        source "$CURRENT_SCRIPT_DIRECTORY/venv/activate"
    fi
fi

bgs-tool $*