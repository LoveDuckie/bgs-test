#!/usr/bin/env bash
<<EOF

   Tool \ Shell Scripts \ Run \ Format

   Run formatting on code project to ensure compliance with PEP8.

EOF
CURRENT_SCRIPT_DIRECTORY=${CURRENT_SCRIPT_DIRECTORY:-$(dirname $(realpath ${BASH_SOURCE[0]:-${(%):-%x}}))}
export SHARED_EXT_SCRIPTS_PATH=${SHARED_EXT_SCRIPTS_PATH:-$(realpath $CURRENT_SCRIPT_DIRECTORY)}
export CURRENT_SCRIPT_FILENAME=${CURRENT_SCRIPT_FILENAME:-$(basename ${BASH_SOURCE[0]:-${(%):-%x}})}
export CURRENT_SCRIPT_FILENAME_BASE=${CURRENT_SCRIPT_FILENAME%.*}
. "$SHARED_EXT_SCRIPTS_PATH/shared_functions.sh"
write_header

write_info "run_format" "Install Dependencies: \"$CURRENT_SCRIPT_DIRECTORY\""
poetry -C "$CURRENT_SCRIPT_DIRECTORY" install
if ! write_response "run_format" "Install Dependencies: $CURRENT_SCRIPT_DIRECTORY"; then
   write_error "run_format" "Failed: Unable to install the dependencies \"$CURRENT_SCRIPT_DIRECTORY\""
   exit 1
fi

write_info "run_format" "Formatting: \"$CURRENT_SCRIPT_DIRECTORY\""
poetry -C "$CURRENT_SCRIPT_DIRECTORY" run black .
if ! write_response "run_format" "Run Black: Format \"$CURRENT_SCRIPT_DIRECTORY\""; then
   write_error "run_format" "Failed: Unable to run unit tests."
   exit 2
fi

write_success "run_format" "Done"
exit 0