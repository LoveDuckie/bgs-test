#!/usr/bin/env bash
<<EOF

   Tool \ Shell Scripts \ Run \ Lint

   Run linting operations to ensure conformity with PEP-8.

EOF
CURRENT_SCRIPT_DIRECTORY=${CURRENT_SCRIPT_DIRECTORY:-$(dirname $(realpath ${BASH_SOURCE[0]:-${(%):-%x}}))}
export SHARED_EXT_SCRIPTS_PATH=${SHARED_EXT_SCRIPTS_PATH:-$(realpath $CURRENT_SCRIPT_DIRECTORY)}
export CURRENT_SCRIPT_FILENAME=${CURRENT_SCRIPT_FILENAME:-$(basename ${BASH_SOURCE[0]:-${(%):-%x}})}
export CURRENT_SCRIPT_FILENAME_BASE=${CURRENT_SCRIPT_FILENAME%.*}
. "$SHARED_EXT_SCRIPTS_PATH/shared_functions.sh"
write_header

write_info "run_lint" "Install Dependencies: \"$CURRENT_SCRIPT_DIRECTORY\""
poetry -C "$CURRENT_SCRIPT_DIRECTORY" install
if ! write_response "run_lint" "Install Dependencies: $CURRENT_SCRIPT_DIRECTORY"; then
   write_error "run_lint" "Failed: Unable to install the dependencies \"$CURRENT_SCRIPT_DIRECTORY\""
   exit 1
fi

write_info "run_lint" "Linting: \"$CURRENT_SCRIPT_DIRECTORY\""
poetry -C "$CURRENT_SCRIPT_DIRECTORY" run pylint --fail-under=8.0 .
if ! write_response "run_lint" "Lint: $CURRENT_SCRIPT_DIRECTORY"; then
   write_error "run_lint" "Failed: Unable to lint $CURRENT_SCRIPT_DIRECTORY"
   exit 1
fi

write_success "run_lint" "Done"
exit 0