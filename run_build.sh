#!/usr/bin/env bash
<<EOF

   Tool \ Shell Scripts \ Run \ Build

   Build the Python package for distribution

EOF
CURRENT_SCRIPT_DIRECTORY=${CURRENT_SCRIPT_DIRECTORY:-$(dirname $(realpath ${BASH_SOURCE[0]:-${(%):-%x}}))}
export SHARED_EXT_SCRIPTS_PATH=${SHARED_EXT_SCRIPTS_PATH:-$(realpath $CURRENT_SCRIPT_DIRECTORY)}
export CURRENT_SCRIPT_FILENAME=${CURRENT_SCRIPT_FILENAME:-$(basename ${BASH_SOURCE[0]:-${(%):-%x}})}
export CURRENT_SCRIPT_FILENAME_BASE=${CURRENT_SCRIPT_FILENAME%.*}
. "$SHARED_EXT_SCRIPTS_PATH/shared_functions.sh"
write_header

if [ -d "$CURRENT_SCRIPT_DIRECTORY/dist" ]; then
   write_warning "run_build" "Cleaning: \"$CURRENT_SCRIPT_DIRECTORY/dist\""
   rm -rf "$CURRENT_SCRIPT_DIRECTORY/dist"
fi

write_info "run_build" "Installing Dependencies: \"$CURRENT_SCRIPT_DIRECTORY\""
poetry -C "$CURRENT_SCRIPT_DIRECTORY" install
if ! write_response "run_build" "Install Dependencies: $CURRENT_SCRIPT_DIRECTORY"; then
   write_error "run_build" "Failed: Unable to build \"$CURRENT_SCRIPT_DIRECTORY\""
   exit 1
fi


write_info "run_build" "Building: \"$CURRENT_SCRIPT_DIRECTORY\""
poetry -C "$CURRENT_SCRIPT_DIRECTORY" build 
if ! write_response "run_build" "Build: $CURRENT_SCRIPT_DIRECTORY"; then
   write_error "run_build" "Failed: Unable to build \"$CURRENT_SCRIPT_DIRECTORY\""
   exit 1
fi

write_success "run_build" "Done"
exit 0