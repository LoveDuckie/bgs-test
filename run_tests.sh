#!/usr/bin/env bash
<<EOF

   Tool \ Shell Scripts \ Run \ Tests

   Run the tests in this repository.

EOF
CURRENT_SCRIPT_DIRECTORY=${CURRENT_SCRIPT_DIRECTORY:-$(dirname $(realpath ${BASH_SOURCE[0]:-${(%):-%x}}))}
export SHARED_EXT_SCRIPTS_PATH=${SHARED_EXT_SCRIPTS_PATH:-$(realpath $CURRENT_SCRIPT_DIRECTORY)}
export CURRENT_SCRIPT_FILENAME=${CURRENT_SCRIPT_FILENAME:-$(basename ${BASH_SOURCE[0]:-${(%):-%x}})}
export CURRENT_SCRIPT_FILENAME_BASE=${CURRENT_SCRIPT_FILENAME%.*}
. "$SHARED_EXT_SCRIPTS_PATH/shared_functions.sh"
write_header

write_info "run_tests" "Install Dependencies: \"$CURRENT_SCRIPT_DIRECTORY\""
poetry -C "$CURRENT_SCRIPT_DIRECTORY" install
if ! write_response "run_tests" "Install Dependencies: $CURRENT_SCRIPT_DIRECTORY"; then
   write_error "run_tests" "Failed: Unable to install the dependencies \"$CURRENT_SCRIPT_DIRECTORY\""
   exit 1
fi

write_info "run_tests" "Running unit tests with \"coverage\"."
poetry -C "$CURRENT_SCRIPT_DIRECTORY" run coverage run -m unittest discover -s bgs_tool_tests -p "*.py" || { echo "Tests failed"; exit 1; }
if ! write_response "run_lint" "Run Coverage: Unit tests"; then
   write_error "run_lint" "Failed: Unable to run unit tests."
   exit 2
fi

write_info "run_tests" "Generating coverage report..."
poetry -C "$CURRENT_SCRIPT_DIRECTORY" run coverage report -m
if ! write_response "run_tests" "Run Unit Tests: $CURRENT_SCRIPT_DIRECTORY"; then
   write_error "run_tests" "Failed: Unable to run the unit tests \"$CURRENT_SCRIPT_DIRECTORY\""
   exit 3
fi

write_info "run_tests" "Generating HTML report..."
poetry -C "$CURRENT_SCRIPT_DIRECTORY" run coverage html
if ! write_response "run_tests" "Generate Coverage Report: $CURRENT_SCRIPT_DIRECTORY"; then
   write_error "run_tests" "Failed: Unable to run the unit tests \"$CURRENT_SCRIPT_DIRECTORY\""
   exit 4
fi

write_success "run_tests" "Done"
exit 0